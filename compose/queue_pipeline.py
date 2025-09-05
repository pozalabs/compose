import asyncio
import enum
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any


class TaskStatus(enum.StrEnum):
    PENDING = enum.auto()
    PROCESSING = enum.auto()
    COMPLETED = enum.auto()
    FAILED = enum.auto()


class Task[T]:
    @property
    def is_failed(self) -> bool:
        return self.status == TaskStatus.FAILED

    @property
    def is_completed(self) -> bool:
        return self.status == TaskStatus.COMPLETED


class TaskQueue[T]:
    def __init__(self, maxsize: int = 100, backpressure_threshold: float = 0.8):
        self._queue = asyncio.Queue(maxsize=maxsize)
        self._maxsize = maxsize
        self._threshold = int(maxsize * backpressure_threshold)
        self._closed = False
        self._finished = False

    async def put(self, item: T) -> bool:
        if self._closed:
            return False

        try:
            await self._queue.put(item)
            return True
        except asyncio.QueueFull:
            return False

    async def get(self) -> T | None:
        if self._finished and self._queue.empty():
            return None

        try:
            return await asyncio.wait_for(self._queue.get(), timeout=0.1)
        except asyncio.TimeoutError:
            return None

    def mark_finished(self):
        self._finished = True

    def close(self):
        self._closed = True
        self._finished = True

    @property
    def is_backpressure_active(self) -> bool:
        return self._queue.qsize() > self._threshold

    @property
    def is_finished(self) -> bool:
        return self._finished


class StageWorker[T, U]:
    def __init__(
        self,
        worker_id: int,
        processor: Callable[[T], U],
        input_queue: TaskQueue[Task[T]],
        output_queue: TaskQueue[Task[U]] | None,
        timeout: float = 30.0,
    ):
        self.worker_id = worker_id
        self.processor = processor
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.timeout = timeout
        self._executor: ThreadPoolExecutor | None = None
        self._is_running = False
        self._shutdown_requested = False

    async def start(self):
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._is_running = True

        try:
            await self._work_loop()
        finally:
            if self._executor is not None:
                self._executor.shutdown(wait=True)
                self._executor = None

    async def _work_loop(self):
        while self._is_running and not self._shutdown_requested:
            if self.output_queue and self.output_queue.is_backpressure_active:
                await asyncio.sleep(0.1)
                continue

            if (task := await self.input_queue.get()) is None:
                if self.input_queue.is_finished:
                    break
                continue

            await self._process_task(task)

    async def _process_task(self, task: Task[T]) -> None:
        task.status = TaskStatus.PROCESSING

        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(self._executor, self.processor, task.data)

            processed_task = Task(
                key=task.key,
                data=result,
                status=TaskStatus.COMPLETED,
            )

            if self.output_queue is not None:
                await self.output_queue.put(processed_task)

        except Exception as exc:
            failed_task = Task(
                key=task.key,
                data=task.data,
                status=TaskStatus.FAILED,
                error=exc,
            )

            if self.output_queue is not None:
                await self.output_queue.put(failed_task)

    def request_shutdown(self):
        self._shutdown_requested = True
        self._is_running = False


class QueueBasedStage[T, U]:
    def __init__(
        self,
        name: str,
        processor: Callable[[T], U],
        worker_count: int,
        input_queue: TaskQueue[Task[T]],
        output_queue: TaskQueue[Task[U]] | None = None,
        timeout: float = 30.0,
    ):
        self.name = name
        self.processor = processor
        self.worker_count = worker_count
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.timeout = timeout

        self.workers = [
            StageWorker(
                worker_id=i,
                processor=processor,
                input_queue=input_queue,
                output_queue=output_queue,
                timeout=timeout,
            )
            for i in range(worker_count)
        ]

        self._worker_tasks: list[asyncio.Task] = []

    async def start(self):
        async with asyncio.TaskGroup() as tg:
            [tg.create_task(worker.start()) for worker in self.workers]

        if self.output_queue is not None:
            self.output_queue.mark_finished()

    def request_shutdown(self):
        for worker in self.workers:
            worker.request_shutdown()


@dataclass
class StageConfig[T, U]:
    name: str
    processor: Callable[[T], U]
    worker_count: int = 1
    queue_size: int = 100
    timeout: float = 30.0
    backpressure_threshold: float = 0.8


@dataclass
class PipelineResult[T]:
    tasks: list[Task[T]]


class QueueBasedPipeline[T]:
    def __init__(self, stages: list[StageConfig], execution_timeout: float = 300.0):
        if not stages:
            raise ValueError("Pipeline requires at least one stage")

        self.stage_configs = stages
        self.execution_timeout = execution_timeout
        self.queues: list[TaskQueue] = []
        self.stages: list[QueueBasedStage] = []

        self._setup_pipeline()

    def _setup_pipeline(self):
        for i, config in enumerate(self.stage_configs):
            queue = TaskQueue(
                maxsize=config.queue_size, backpressure_threshold=config.backpressure_threshold
            )
            self.queues.append(queue)

        final_queue = TaskQueue(
            maxsize=self.stage_configs[-1].queue_size,
            backpressure_threshold=self.stage_configs[-1].backpressure_threshold,
        )
        self.queues.append(final_queue)

        for i, config in enumerate(self.stage_configs):
            input_queue = self.queues[i]
            output_queue = self.queues[i + 1] if i + 1 < len(self.queues) else None

            stage = QueueBasedStage(
                name=config.name,
                processor=config.processor,
                worker_count=config.worker_count,
                input_queue=input_queue,
                output_queue=output_queue,
                timeout=config.timeout,
            )
            self.stages.append(stage)

    async def execute(self, tasks: list[Task[T]]) -> PipelineResult[Any]:
        try:
            return await self._run_pipeline(tasks)
        except Exception:
            raise
        finally:
            for stage in self.stages:
                stage.request_shutdown()

            for queue in self.queues:
                queue.close()

    async def _run_pipeline(self, tasks: list[Task[T]]) -> PipelineResult[Any]:
        input_queue = self.queues[0]
        for task in tasks:
            await input_queue.put(task)

        input_queue.mark_finished()

        stage_tasks = [asyncio.create_task(stage.start()) for stage in self.stages]

        result_collection_task = asyncio.create_task(self._collect_results(len(tasks)))

        try:
            results, *_ = await asyncio.wait_for(
                asyncio.gather(result_collection_task, *stage_tasks, return_exceptions=True),
                timeout=self.execution_timeout,
            )

        except asyncio.TimeoutError:
            results = []

        return PipelineResult(
            tasks=results if isinstance(results, list) else [],
        )

    async def _collect_results(self, expected_count: int) -> list[Task]:
        results = []
        output_queue = self.queues[-1]

        while len(results) < expected_count:
            task = await output_queue.get()
            if task is None:
                if output_queue.is_finished:
                    break
                continue

            results.append(task)

        return results

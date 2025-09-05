import asyncio
import time
from collections.abc import AsyncIterator, Callable
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task(Generic[T]):
    id: str
    data: T
    status: TaskStatus = TaskStatus.PENDING
    stage_results: dict[str, Any] = field(default_factory=dict)
    error: Exception | None = None
    created_at: float = field(default_factory=time.time)

    @property
    def is_failed(self) -> bool:
        return self.status == TaskStatus.FAILED

    @property
    def is_completed(self) -> bool:
        return self.status == TaskStatus.COMPLETED


@dataclass
class StageMetrics:
    name: str
    processed_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_processing_time: float = 0.0

    @property
    def success_rate(self) -> float:
        if self.processed_count == 0:
            return 0.0
        return self.success_count / self.processed_count

    @property
    def avg_processing_time(self) -> float:
        if self.processed_count == 0:
            return 0.0
        return self.total_processing_time / self.processed_count


@dataclass
class PipelineResult(Generic[T]):
    tasks: list[Task[T]]
    metrics: dict[str, StageMetrics]
    total_duration: float
    success_count: int = 0
    failed_count: int = 0

    def __post_init__(self):
        self.success_count = sum(1 for task in self.tasks if task.is_completed)
        self.failed_count = sum(1 for task in self.tasks if task.is_failed)


class WorkerPool(Generic[T, U]):
    def __init__(self, worker_count: int, processor: Callable[[T], U]):
        self.worker_count = worker_count
        self.processor = processor
        self._executor: ThreadPoolExecutor | None = None
        self._semaphore = asyncio.Semaphore(worker_count)

    async def __aenter__(self):
        self._executor = ThreadPoolExecutor(max_workers=self.worker_count)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None

    async def process(self, data: T) -> U:
        if self._executor is None:
            raise RuntimeError("WorkerPool not initialized - use async context manager")

        async with self._semaphore:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self._executor, self.processor, data)


class StageProcessor(Generic[T, U]):
    def __init__(
        self, name: str, processor: Callable[[T], U], worker_count: int = 1, timeout: float = 30.0
    ):
        self.name = name
        self.processor = processor
        self.worker_count = worker_count
        self.timeout = timeout
        self.metrics = StageMetrics(name)
        self._shutdown_requested = False

    async def process_stream(self, input_stream: AsyncIterator[Task[T]]) -> AsyncIterator[Task[U]]:
        async with WorkerPool(self.worker_count, self.processor) as pool:
            async for task in input_stream:
                if self._shutdown_requested:
                    break

                yield await self._process_task(task, pool)

    async def _process_task(self, task: Task[T], pool: WorkerPool[T, U]) -> Task[U]:
        start_time = time.time()
        task.status = TaskStatus.PROCESSING

        try:
            result = await asyncio.wait_for(pool.process(task.data), timeout=self.timeout)

            processed_task = Task(
                id=task.id,
                data=result,
                status=TaskStatus.COMPLETED,
                stage_results=task.stage_results.copy(),
                created_at=task.created_at,
            )
            processed_task.stage_results[self.name] = result

            self.metrics.success_count += 1
            return processed_task

        except Exception as error:
            failed_task = Task(
                id=task.id,
                data=task.data,
                status=TaskStatus.FAILED,
                stage_results=task.stage_results.copy(),
                error=error,
                created_at=task.created_at,
            )

            self.metrics.error_count += 1
            return failed_task

        finally:
            processing_time = time.time() - start_time
            self.metrics.total_processing_time += processing_time
            self.metrics.processed_count += 1

    def request_shutdown(self):
        self._shutdown_requested = True


@dataclass
class StageConfig(Generic[T, U]):
    name: str
    processor: Callable[[T], U]
    worker_count: int = 1
    timeout: float = 30.0


class ExecutionContext:
    def __init__(self, timeout: float = 300.0):
        self.timeout = timeout
        self.start_time = time.time()
        self._shutdown_event = asyncio.Event()

    @property
    def elapsed_time(self) -> float:
        return time.time() - self.start_time

    @property
    def is_timeout_exceeded(self) -> bool:
        return self.elapsed_time > self.timeout

    def request_shutdown(self):
        self._shutdown_event.set()

    @property
    def shutdown_requested(self) -> bool:
        return self._shutdown_event.is_set()


class Pipeline(Generic[T]):
    def __init__(self, stages: list[StageConfig], execution_timeout: float = 300.0):
        if not stages:
            raise ValueError("Pipeline requires at least one stage")

        self.stages = [
            StageProcessor(stage.name, stage.processor, stage.worker_count, stage.timeout)
            for stage in stages
        ]
        self.execution_timeout = execution_timeout

    async def execute(self, tasks: list[Task[T]]) -> PipelineResult[Any]:
        async with self._create_execution_context() as context:
            try:
                return await self._run_pipeline(tasks, context)
            except Exception as error:
                await self._handle_pipeline_error(error, context)
                raise

    @asynccontextmanager
    async def _create_execution_context(self):
        context = ExecutionContext(self.execution_timeout)
        try:
            yield context
        finally:
            context.request_shutdown()
            for stage in self.stages:
                stage.request_shutdown()

    async def _run_pipeline(
        self, tasks: list[Task[T]], context: ExecutionContext
    ) -> PipelineResult[Any]:
        print(f"Starting pipeline with {len(tasks)} tasks across {len(self.stages)} stages")

        # Create input stream
        current_stream = self._create_input_stream(tasks)

        # Chain stages together
        for stage in self.stages:
            print(f"Connecting stage: {stage.name}")
            current_stream = stage.process_stream(current_stream)

        # Collect results
        results = []
        async for result_task in current_stream:
            if context.is_timeout_exceeded or context.shutdown_requested:
                print("Pipeline execution timeout or shutdown requested")
                break

            results.append(result_task)
            print(f"Completed task {result_task.id} with status {result_task.status.value}")

        return PipelineResult(
            tasks=results,
            metrics={stage.name: stage.metrics for stage in self.stages},
            total_duration=context.elapsed_time,
        )

    async def _create_input_stream(self, tasks: list[Task[T]]) -> AsyncIterator[Task[T]]:
        for task in tasks:
            yield task

    async def _handle_pipeline_error(self, error: Exception, context: ExecutionContext):
        print(f"Pipeline error after {context.elapsed_time:.2f}s: {error}")
        # Log error, cleanup resources, etc.

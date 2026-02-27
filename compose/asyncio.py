import asyncio
from collections.abc import Awaitable, Callable, Hashable


class AsyncJob[K: Hashable, **P, T]:
    def __init__(
        self,
        key: K,
        func: Callable[P, Awaitable[T]],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        self.key = key
        self.func = func
        self.args = args
        self.kwargs = kwargs


class AsyncTaskExecutor:
    def __init__(self, concurrency: int, timeout: float | None = None):
        self.concurrency = concurrency
        self.timeout = timeout

    async def execute[K, **P, T](
        self,
        jobs: list[AsyncJob[K, P, T]],
        concurrency: int | None = None,
        timeout: float | None = None,
    ) -> dict[K, T]:
        concurrency = concurrency if concurrency is not None else self.concurrency
        timeout = timeout if timeout is not None else self.timeout

        coro = _execute_jobs(jobs=jobs, semaphore=asyncio.Semaphore(concurrency))

        if timeout is None:
            return await coro

        async with asyncio.timeout(timeout):
            return await coro


async def _execute_jobs[K, **P, T](
    jobs: list[AsyncJob[K, P, T]],
    semaphore: asyncio.Semaphore,
) -> dict[K, T]:
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = [
                (job.key, tg.create_task(_execute_job(job=job, semaphore=semaphore)))
                for job in jobs
            ]
    except* Exception as eg:
        raise eg.exceptions[0]

    return {key: task.result() for key, task in tasks}


async def _execute_job[K, **P, T](job: AsyncJob[K, P, T], semaphore: asyncio.Semaphore) -> T:
    async with semaphore:
        return await job.func(*job.args, **job.kwargs)

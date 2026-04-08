import collections
import concurrent.futures
from collections.abc import Callable, Hashable
from typing import Self


class DAGJob[K: Hashable, T]:
    def __init__(
        self,
        key: K,
        dependencies: set[K],
        func: Callable[[dict[K, T]], T],
    ):
        self.key = key
        self.dependencies = dependencies
        self.func = func

    @classmethod
    def bound[**P](
        cls,
        key: K,
        func: Callable[P, T],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Self:
        return cls(
            key=key,
            dependencies=set(),
            func=lambda _: func(*args, **kwargs),
        )


class DAGExecutor:
    def __init__(self, max_workers: int, timeout: int | None = None):
        self.max_workers = max_workers
        self.timeout = timeout

    def execute[K, T](
        self,
        jobs: list[DAGJob[K, T]],
        max_workers: int | None = None,
        timeout: int | None = None,
    ) -> dict[K, T]:
        if not jobs:
            return {}

        max_workers = max_workers or self.max_workers

        job_map = {job.key: job for job in jobs}
        dependencies = {job.key: job.dependencies for job in jobs}
        dependents = self._build_dependents(dependencies)

        completed = {}
        ready_queue = self._get_ready_queue(jobs)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            active_futures = {}

            while len(completed) < len(jobs):
                while ready_queue and len(active_futures) < max_workers:
                    job_key = ready_queue.popleft()
                    job = job_map[job_key]
                    result = {k: completed[k] for k in job.dependencies}
                    future = executor.submit(job.func, result)
                    active_futures[future] = job_key

                if not active_futures:
                    continue

                done, _ = concurrent.futures.wait(
                    active_futures,
                    return_when=concurrent.futures.FIRST_COMPLETED,
                    timeout=timeout or self.timeout,
                )

                for future in done:
                    job_id = active_futures.pop(future)
                    completed[job_id] = future.result()

                    for dependent_id in dependents.get(job_id, set()):
                        if dependent_id not in completed and dependencies[dependent_id].issubset(
                            completed.keys()
                        ):
                            ready_queue.append(dependent_id)

        return completed

    @staticmethod
    def _get_ready_queue[K, T](jobs: list[DAGJob[K, T]]) -> collections.deque[K]:
        ready_queue = collections.deque()
        for job in jobs:
            if not job.dependencies:
                ready_queue.append(job.key)
        return ready_queue

    @staticmethod
    def _build_dependents[K](dependencies: dict[K, set[K]]) -> dict[K, set[K]]:
        dependents = collections.defaultdict(set)
        for key, deps in dependencies.items():
            for dep in deps:
                dependents[dep].add(key)
        return dict(dependents)

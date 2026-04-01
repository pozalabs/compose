import collections
import concurrent.futures
from collections.abc import Callable, Hashable
from typing import Self


class DAGJob[K: Hashable, **P, T]:
    def __init__(
        self,
        key: K,
        dependencies: set[K],
        func: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        self.key = key
        self.dependencies = dependencies
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def no_dependencies(
        cls,
        key: K,
        func: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Self:
        return cls(
            key=key,
            dependencies=set(),
            func=func,
            *args,  # type: ignore[bad-argument-type]
            **kwargs,
        )


class DAGExecutor:
    def __init__(self, max_workers: int, timeout: int | None = None):
        self.max_workers = max_workers
        self.timeout = timeout

    def execute[K, **P, T](
        self,
        jobs: list[DAGJob[K, P, T]],
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
                    future = executor.submit(job.func, *job.args, **job.kwargs)  # type: ignore[bad-argument-type]
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

                    # 완료된 작업에 의존하는 작업 중 모든 의존성이 충족된 작업만 확인
                    # dependencies = {"A": set(), "B": set(), "C": {"A"}, "D": {"A", "B"}, "E": {"C", "D"}}
                    # dependents = {"A": {"C", "D"}, "B": {"D"}, "C": {"E"}, "D": {"E"}}
                    # 1. completed = {}, ready_queue = [A, B]
                    # 2. A 완료 -> completed = {"A": "result_A"}, dependents.get("A") = {"C", "D"}
                    #    dependencies["C"] = {"A"} ⊆ completed.keys() -> ready_queue.append("C")
                    #    dependencies["D"] = {"A", "B"} ⊈ completed.keys() -> X
                    # 3. B 완료 -> completed = {"A": "result_A", "B": "result_B"}, dependents.get("B") = {"D"}
                    #    dependencies["D"] = {"A", "B"} ⊆ completed.keys() -> ready_queue.append("D")
                    # C, D, E도 같은 방식으로 처리
                    for dependent_id in dependents.get(job_id, set()):
                        if dependent_id not in completed and dependencies[dependent_id].issubset(
                            completed.keys()
                        ):
                            ready_queue.append(dependent_id)

        return completed

    @staticmethod
    def _get_ready_queue[K, **P, T](jobs: list[DAGJob[K, P, T]]) -> collections.deque[K]:
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

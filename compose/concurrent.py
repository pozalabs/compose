import concurrent.futures
import functools
from collections.abc import Callable, Hashable


def execute_in_pool[K, T](
    pool_factory: Callable[[], concurrent.futures.Executor],
    funcs: dict[K, functools.partial[T]],
    timeout: int | None = None,
) -> dict[K, T | Exception]:
    results: dict[K, T | Exception] = {}
    with pool_factory() as executor:
        future_to_key: dict[concurrent.futures.Future[T], K] = {}
        for key, func in funcs.items():
            future = executor.submit(func)
            future_to_key[future] = key

        for future in concurrent.futures.as_completed(future_to_key, timeout=timeout):
            try:
                results[future_to_key[future]] = future.result()
            except Exception as exc:
                results[future_to_key[future]] = exc

    return results


class ThreadPoolJob[K: Hashable, **P, T]:
    def __init__(
        self,
        key: K,
        func: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        self.key = key
        self.func = func
        self.args = args
        self.kwargs = kwargs


class ThreadPoolExecutor:
    def __init__(self, max_workers: int, timeout: int | None = None):
        self.max_workers = max_workers
        self.timeout = timeout

    def execute[K, **P, T](
        self,
        jobs: list[ThreadPoolJob[K, P, T]],
        max_workers: int | None = None,
        timeout: int | None = None,
    ) -> dict[K, T | Exception]:
        results: dict[K, T | Exception] = {}
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers or self.max_workers
        ) as executor:
            future_to_key: dict[concurrent.futures.Future[T], K] = {}

            for job in jobs:
                future = executor.submit(functools.partial(job.func, *job.args, **job.kwargs))
                future_to_key[future] = job.key

            for future in concurrent.futures.as_completed(
                future_to_key, timeout=timeout or self.timeout
            ):
                try:
                    results[future_to_key[future]] = future.result()
                except Exception as exc:
                    results[future_to_key[future]] = exc

        return results

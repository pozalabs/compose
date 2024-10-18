import concurrent.futures
import functools
from collections.abc import Callable


def execute_in_pool[K, T](
    pool_factory: Callable[[], concurrent.futures.Executor],
    funcs: dict[K, functools.partial[T]],
    timeout: int | None = None,
) -> dict[K, T]:
    result = {}
    with pool_factory() as executor:
        future_to_key = dict()
        for key, func in funcs.items():
            future = executor.submit(func)
            future_to_key[future] = key

        for future in concurrent.futures.as_completed(future_to_key, timeout=timeout):
            result[future_to_key[future]] = future.result()

    return result

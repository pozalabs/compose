import concurrent.futures
import functools
from collections.abc import Callable
from typing import TypeVar

K = TypeVar("K")
T = TypeVar("T")


def execute_in_pool(
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

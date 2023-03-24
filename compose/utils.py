import functools
import warnings
from collections.abc import Callable
from typing import Any


def deprecated(message: str, stack_level: int = 1):
    def wrapper(func: Callable[..., Any]):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            warnings.warn(message, DeprecationWarning, stacklevel=stack_level)
            return func(*args, **kwargs)

        return inner

    return wrapper

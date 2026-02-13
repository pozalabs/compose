from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, Self

from .. import constants
from . import primitive


def _require_int(func: Callable[[type[Byte], Any], Byte]) -> Callable[[type[Byte], Any], Byte]:
    @functools.wraps(func)
    def wrapper(cls, v: Any, /) -> Byte:
        if not isinstance(v, int):
            raise TypeError(f"`{cls.__name__}.{func.__name__}` expects int, got {type(v).__name__}")
        return func(cls, v)

    return wrapper


class Byte(primitive.Int):
    def __new__(cls, v: Any, /) -> Self:
        v = super().__new__(cls, v)
        if v < 0:
            raise ValueError(f"`{cls.__name__}` must be a non-negative integer")
        return v

    @classmethod
    @_require_int
    def from_mib(cls, v: int, /) -> Self:
        return cls(v * constants.Unit.MIB)

    @classmethod
    @_require_int
    def from_gib(cls, v: int, /) -> Self:
        return cls(v * constants.Unit.GIB)

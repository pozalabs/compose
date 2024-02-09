from collections.abc import Callable
from typing import TypeVar

from .base import Operator

T = TypeVar("T")


class _ForEach:
    def __call__(self, inputs: list[T], callback: Callable[[T], Operator]) -> list[Operator]:
        return [callback(inp) for inp in inputs]


ForEach = _ForEach()

from collections.abc import Callable, Iterable
from typing import TypeVar

from .base import Operator

T = TypeVar("T")


class _Map:
    def __call__(
        self, collection: Iterable[T], callback: Callable[[T], Operator], /
    ) -> list[Operator]:
        return [callback(item) for item in collection]


Map = _Map()

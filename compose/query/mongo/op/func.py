from collections.abc import Callable, Iterable
from typing import TypeVar

from .base import Operator

T = TypeVar("T")


class _Map:
    def __init__(self, collection: Iterable[T], callback: Callable[[T], Operator]):
        self.collection = collection
        self.callback = callback

    def __call__(self) -> list[Operator]:
        return [self.callback(item) for item in self.collection]


def Map(collection: Iterable[T], callback: Callable[[T], Operator]) -> list[Operator]:  # noqa: N802
    return _Map(collection, callback)()

from collections.abc import Callable, Iterable
from typing import TypeVar

from .base import Operator

T = TypeVar("T")


class _Map:
    def __init__(self, collection: Iterable[T], callback: Callable[[T], Operator]):
        self.collection = collection
        self.callback = callback

    def eval(self) -> list[Operator]:
        return [self.callback(item) for item in self.collection]


def Map(collection: Iterable[T], callback: Callable[[T], Operator]) -> list[Operator]:  # noqa: N802
    return _Map(collection, callback).eval()


class _Filter:
    def __init__(self, collection: list[Operator], predicate: Callable[[Operator], bool]):
        self.collection = collection
        self.predicate = predicate

    def eval(self) -> list[Operator]:
        return [item for item in self.collection if self.predicate(item)]


def Filter(collection: list[Operator], predicate: Callable[[Operator], bool]) -> list[Operator]:  # noqa: N802
    return _Filter(collection, predicate=predicate).eval()


class NonEmpty:
    def __call__(self, op: Operator) -> bool:
        return bool(op.expression())

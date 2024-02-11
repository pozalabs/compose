from collections.abc import Callable, Iterable
from typing import Self, TypeVar

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

    @classmethod
    def non_empty(cls, *ops: Operator) -> Self:
        return cls(*ops, predicate=lambda op: op.expression())


def Filter(*ops: Operator, predicate: Callable[[Operator], bool]) -> list[Operator]:  # noqa: N802
    return _Filter(*ops, predicate=predicate).eval()

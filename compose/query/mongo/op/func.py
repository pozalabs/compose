from collections.abc import Callable, Iterable
from typing import TypeAlias, TypeVar

from .base import Operator
from .raw import Raw
from .types import DictExpression, ListExpression

T = TypeVar("T")
Expressionable: TypeAlias = Operator | DictExpression | ListExpression


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


class _Flatten:
    def __init__(self, ops: Iterable[Expressionable]):
        self.ops = list(ops)

    def eval(self) -> list[Operator]:
        result = []
        for op in self.ops:
            exp = op.expression() if isinstance(op, Operator) else op

            match exp:
                case dict():
                    result.append(Raw(exp))
                case list():
                    for e in exp:
                        result.extend([Raw(e)] if isinstance(e, dict) else self.__class__(e).eval())
                case _:
                    raise ValueError(f"Expression must be dict or list, not {type(exp)} ({exp})")

        return result


def Flatten(ops: Iterable[Expressionable]) -> list[Operator]:  # noqa: N802
    return _Flatten(ops).eval()

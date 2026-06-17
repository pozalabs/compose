from collections.abc import Callable

from .base import Merge, Operator
from .pipeline import Pipeline as _Pipeline
from .types import DictExpression, ListExpression


def _non_empty(op: Operator) -> bool:
    return bool(op.expression())


class _Filter:
    def __init__(
        self, collection: list[Operator], predicate: Callable[[Operator], bool] = _non_empty
    ):
        self.collection = collection
        self.predicate = predicate

    def eval(self) -> list[Operator]:
        return [item for item in self.collection if self.predicate(item)]


def Filter(
    collection: list[Operator], predicate: Callable[[Operator], bool] = _non_empty
) -> list[Operator]:
    return _Filter(collection, predicate=predicate).eval()


def Q(*ops: *tuple[Operator, ...]) -> DictExpression:
    return Merge.into_dict(*ops).expression()


def Pipeline(*ops: *tuple[Operator, ...]) -> ListExpression:
    return _Pipeline(*ops).expression()

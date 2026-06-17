from .base import Merge, Operator
from .pipeline import Pipeline as _Pipeline
from .types import DictExpression, ListExpression


def query(*ops: *tuple[Operator, ...]) -> DictExpression:
    return Merge.into_dict(*ops).expression()


def pipeline(*ops: *tuple[Operator, ...]) -> ListExpression:
    return _Pipeline(*ops).expression()

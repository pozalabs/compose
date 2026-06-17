from typing import Any

from ..base import Operator, evaluate
from ..types import DictExpression
from .base import GeneralAggregationOperator


class SetUnion(GeneralAggregationOperator):
    mongo_operator = "$setUnion"


class SetIntersection(Operator):
    def __init__(self, *values: Any):
        self.values = list(values)

    def expression(self) -> DictExpression:
        return {"$setIntersection": [evaluate(v) for v in self.values]}

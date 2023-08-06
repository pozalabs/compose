from typing import Any

from ..base import GeneralAggregationOperator, Operator
from ..types import DictExpression


class Concat(GeneralAggregationOperator):
    mongo_operator = "$concat"


class ToString(Operator):
    def __init__(self, expr: Any):
        self.expr = expr

    def expression(self) -> DictExpression:
        return {"$toString": self.expr}

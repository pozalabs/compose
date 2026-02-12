from typing import Any

from ..base import GeneralAggregationOperator, Operator, evaluate
from ..types import DictExpression


class Concat(GeneralAggregationOperator):
    mongo_operator = "$concat"


class Split(Operator):
    def __init__(self, expr: Any, delimiter: str):
        self.expr = expr
        self.delimiter = delimiter

    def expression(self) -> DictExpression:
        return {"$split": [evaluate(self.expr), self.delimiter]}

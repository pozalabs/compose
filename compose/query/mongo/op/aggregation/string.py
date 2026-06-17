from typing import Any

from ..base import Operator, evaluate
from ..types import DictExpression
from .base import GeneralAggregationOperator


class Concat(GeneralAggregationOperator):
    mongo_operator = "$concat"


class Split(Operator):
    def __init__(self, expr: Any, delimiter: str):
        self.expr = expr
        self.delimiter = delimiter

    def expression(self) -> DictExpression:
        return {"$split": [evaluate(self.expr), self.delimiter]}


class RegexMatch(Operator):
    def __init__(self, field: Any, value: Any):
        self.field = field
        self.value = value

    def expression(self) -> DictExpression:
        return {"$regexMatch": {"input": evaluate(self.field), "regex": evaluate(self.value)}}

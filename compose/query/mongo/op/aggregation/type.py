from typing import Any

from ..base import Operator, evaluate
from ..types import DictExpression


class ToString(Operator):
    def __init__(self, expr: Any):
        self.expr = expr

    def expression(self) -> DictExpression:
        return {"$toString": evaluate(self.expr)}


class ToBool(Operator):
    def __init__(self, expression: Any):
        self._expression = expression

    def expression(self) -> DictExpression:
        return {"$toBool": evaluate(self._expression)}


class ToInt(Operator):
    def __init__(self, expression: Any):
        self._expression = expression

    def expression(self) -> DictExpression:
        return {"$toInt": evaluate(self._expression)}

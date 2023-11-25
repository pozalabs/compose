from typing import Any

from ..base import Evaluable, Operator
from ..types import DictExpression


class ToBool(Operator):
    def __init__(self, expression: Any):
        self._expression = expression

    def expression(self) -> DictExpression:
        return {"$toBool": Evaluable(self._expression).expression()}

from typing import Any

from ..base import DictExpression, Evaluable, Operator


class First(Operator):
    def __init__(self, expression: Any, /):
        self._expression = expression

    def expression(self) -> DictExpression:
        return {"$first": Evaluable(self._expression).expression()}

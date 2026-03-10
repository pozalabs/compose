from typing import Generic

from .base import Operator, deep_evaluate
from .types import Expression


class Raw(Generic[Expression], Operator):
    def __init__(self, expression: Expression):
        self._expression = expression  # type: ignore

    def expression(self) -> Expression:
        return deep_evaluate(self._expression)

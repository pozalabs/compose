from typing import Any

from .base import Evaluable, Operator
from .types import DictExpression


class Expr(Operator):
    def __init__(self, op: Any):
        self.op = op

    def expression(self) -> DictExpression:
        return Evaluable(self.op).expression()

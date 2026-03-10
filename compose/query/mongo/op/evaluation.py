from typing import Any

from .base import Operator, evaluate
from .types import DictExpression


class Expr(Operator):
    def __init__(self, op: Any):
        self.op = op

    def expression(self) -> DictExpression:
        return {"$expr": evaluate(self.op)}

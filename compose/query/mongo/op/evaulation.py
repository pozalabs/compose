from .base import Operator
from .types import DictExpression


class Expr(Operator):
    def __init__(self, op: Operator):
        self.op = op

    def expression(self) -> DictExpression:
        return {"$expr": self.op.expression()}

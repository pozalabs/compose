from __future__ import annotations

from typing import Any, Optional

from .base import Operator
from .comparison import ComparisonOperator


class Expr(Operator):
    def __init__(self, op: Operator):
        self.op = op

    def expression(self) -> dict[str, Any]:
        return {"$expr": self.op.expression()}


class AEqual(ComparisonOperator):
    def __init__(self, field: str, value: Optional[Any] = None):
        super().__init__(field=field, value=value)

    def expression(self) -> dict[str, Any]:
        return {"$eq": [self.field, self.value]}

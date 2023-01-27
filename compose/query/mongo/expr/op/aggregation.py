from __future__ import annotations

from typing import Any, Optional

from ..base import Expression
from .comparison import ComparisonOperator


class Expr(Expression):
    def __init__(self, op: Expression):
        self.op = op

    def expression(self) -> dict[str, Any]:
        return {"$expr": self.op.expression()}


class AEqual(ComparisonOperator):
    def __init__(self, field: str, value: Optional[Any] = None, compare_none: bool = False):
        super().__init__(field=field, value=value, compare_none=compare_none)

    def get_expression(self) -> dict[str, Any]:
        return {"$eq": [self.field, self.value]}

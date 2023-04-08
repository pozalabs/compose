from __future__ import annotations

from collections.abc import Callable
from typing import Any, Optional

from . import utils
from .base import ComparisonOperator, Operator
from .types import DictExpression


class EmptyOnNull(Operator):
    def __init__(self, op: ComparisonOperator):
        self.op = op

    def expression(self) -> dict[str, Any]:
        return self.op.expression() if self.op.value is not None else {}


def _expression_factory(mongo_operator: str) -> Callable[[ComparisonOperator], DictExpression]:
    def expression(self: ComparisonOperator) -> DictExpression:
        return {self.field: {mongo_operator: self.value}}

    return expression


def create_comparison_operator(name: str, mongo_operator: str) -> type[ComparisonOperator]:
    return utils.create_operator(
        name=name,
        base=(ComparisonOperator,),
        expression_factory=_expression_factory(mongo_operator),
    )


Eq = create_comparison_operator(name="Eq", mongo_operator="$eq")
Ne = create_comparison_operator(name="Ne", mongo_operator="$ne")
Gt = create_comparison_operator(name="Gt", mongo_operator="$gt")
Gte = create_comparison_operator(name="Gte", mongo_operator="$gte")
Lt = create_comparison_operator(name="Lt", mongo_operator="$lt")
Lte = create_comparison_operator(name="Lte", mongo_operator="$lte")
In = create_comparison_operator(name="In", mongo_operator="$in")
Nin = create_comparison_operator(name="Nin", mongo_operator="$nin")


class Regex(ComparisonOperator):
    def __init__(
        self,
        field: str,
        value: Optional[Any] = None,
        options: str = "ms",
    ):
        super().__init__(field=field, value=value)
        self.options = options

    def expression(self) -> dict[str, Any]:
        return {self.field: {"$regex": self.value, "$options": self.options}}

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .. import DictExpression, utils
from ..base import Operator
from ..comparison import ComparisonOperator


class Expr(Operator):
    def __init__(self, op: Operator):
        self.op = op

    def expression(self) -> dict[str, Any]:
        return {"$expr": self.op.expression()}


def _expression_factory(mongo_operator: str) -> Callable[[ComparisonOperator], DictExpression]:
    def expression(self: ComparisonOperator) -> DictExpression:
        return {mongo_operator: [self.field, self.value]}

    return expression


def create_aggregation_comparison_operator(
    name: str, mongo_operator: str
) -> type[ComparisonOperator]:
    return utils.create_operator(
        name=name,
        base=(ComparisonOperator,),
        expression_factory=_expression_factory(mongo_operator),
    )


AEq = create_aggregation_comparison_operator(name="AEq", mongo_operator="$eq")
ANe = create_aggregation_comparison_operator(name="ANe", mongo_operator="$ne")
AGt = create_aggregation_comparison_operator(name="AGt", mongo_operator="$gt")
AGte = create_aggregation_comparison_operator(name="AGte", mongo_operator="$gte")
ALt = create_aggregation_comparison_operator(name="ALt", mongo_operator="$lt")
ALte = create_aggregation_comparison_operator(name="ALte", mongo_operator="$lte")
AEqual = AEq

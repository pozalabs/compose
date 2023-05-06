from __future__ import annotations

from collections.abc import Callable
from typing import Any, Optional

from .. import utils
from ..base import ComparisonOperator
from ..types import DictExpression


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


class AEqual(ComparisonOperator):
    def __init__(self, field: str, value: Optional[Any] = None):
        super().__init__(field=field, value=value)

    def expression(self) -> DictExpression:
        return {"$eq": [self.field, self.value]}


AEq = create_aggregation_comparison_operator(name="AEq", mongo_operator="$eq")
ANe = create_aggregation_comparison_operator(name="ANe", mongo_operator="$ne")
AGt = create_aggregation_comparison_operator(name="AGt", mongo_operator="$gt")
AGte = create_aggregation_comparison_operator(name="AGte", mongo_operator="$gte")
ALt = create_aggregation_comparison_operator(name="ALt", mongo_operator="$lt")
ALte = create_aggregation_comparison_operator(name="ALte", mongo_operator="$lte")

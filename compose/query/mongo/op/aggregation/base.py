from typing import Any, ClassVar, cast

from ..base import Operator, deep_evaluate
from ..types import DictExpression


class GeneralAggregationOperator(Operator):
    mongo_operator: ClassVar[str] = ""

    def __init__(self, *expressions: Any):
        self.expressions = list(expressions)

    def expression(self) -> DictExpression:
        return deep_evaluate({self.mongo_operator: self.expressions})


def create_general_aggregation_operator(
    name: str, mongo_operator: str
) -> type[GeneralAggregationOperator]:
    return cast(
        type[GeneralAggregationOperator],
        type(name, (GeneralAggregationOperator,), {"mongo_operator": mongo_operator}),
    )

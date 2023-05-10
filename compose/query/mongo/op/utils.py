from collections.abc import Callable
from typing import Any, TypeVar, cast

from .base import GeneralAggregationOperator, Operator

OperatorType = TypeVar("OperatorType", bound=Operator)


def create_operator(
    name: str,
    expression_factory: Callable[[OperatorType], Any],
    base: tuple[type[OperatorType], ...],
) -> type[OperatorType]:
    return cast(
        type[OperatorType],
        type(name, base, {"expression": expression_factory}),
    )


def create_general_aggregation_operator(
    name: str, mongo_operator: str
) -> type[GeneralAggregationOperator]:
    return cast(
        type[GeneralAggregationOperator],
        type(name, (GeneralAggregationOperator,), {"mongo_operator": mongo_operator}),
    )

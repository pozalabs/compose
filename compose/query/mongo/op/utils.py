from collections.abc import Callable
from typing import Any, TypeVar, cast

from .base import Operator

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

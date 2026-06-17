from collections.abc import Callable
from typing import Any, cast

from .base import Operator


def create_operator[T: Operator](
    name: str,
    expression_factory: Callable[[T], Any],
    base: tuple[type[T], ...],
) -> type[T]:
    return cast(
        type[T],
        type(name, base, {"expression": expression_factory}),
    )

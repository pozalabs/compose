from __future__ import annotations

import abc
from typing import Any, cast

from .base import Operator


class LogicalOperator(Operator):
    def __init__(self, *ops: Operator):
        self.ops = list(ops)

    @abc.abstractmethod
    def expression(self) -> dict[str, list[dict[str, Any]]]:
        raise NotImplementedError


def create_operator(name: str, mongo_operator: str) -> type[LogicalOperator]:
    def expression(self) -> dict[str, list[dict[str, Any]]]:
        expressions = [expr for op in self.ops if (expr := op.expression())]
        return {mongo_operator: expressions} if expressions else {}

    return cast(type[LogicalOperator], type(name, (LogicalOperator,), {"expression": expression}))


And = create_operator(name="And", mongo_operator="$and")
Or = create_operator(name="Or", mongo_operator="$or")

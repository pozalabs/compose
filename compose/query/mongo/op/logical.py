from __future__ import annotations

import abc
from typing import Any, cast

from .base import Expression
from .comparison import ComparisonOperator


class LogicalOperator(Expression):
    def __init__(self, *ops: ComparisonOperator):
        self.ops = list(ops)

    @abc.abstractmethod
    def expression(self) -> dict[str, list[dict[str, Any]]]:
        raise NotImplementedError


def create_operator(name: str, mongo_operator: str) -> type[LogicalOperator]:
    def expression(self) -> dict[str, list[dict[str, Any]]]:
        expressions = [expr for op in self.ops if (expr := op.expression())]
        return expressions and {mongo_operator: expressions}

    return cast(type[LogicalOperator], type(name, (LogicalOperator,), {"expression": expression}))


And = create_operator(name="And", mongo_operator="$and")
Or = create_operator(name="or", mongo_operator="$or")

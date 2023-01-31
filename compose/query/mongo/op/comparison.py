from __future__ import annotations

import abc
from typing import Any, Optional, Type, cast

from .base import Operator


class ComparisonOperator(Operator):
    def __init__(self, field: str, value: Optional[Any] = None):
        self.field = field
        self.value = value

    @abc.abstractmethod
    def expression(self) -> dict[str, Any]:
        raise NotImplementedError


class EmptyOnNull(Operator):
    def __init__(self, op: ComparisonOperator):
        self.op = op

    def expression(self) -> dict[str, Any]:
        return self.op.expression() if self.op.value is not None else {}


def create_operator(name: str, mongo_operator: str) -> Type[ComparisonOperator]:
    def expression(self) -> dict[str, Any]:
        return {self.field: {mongo_operator: self.value}}

    return cast(
        Type[ComparisonOperator],
        type(name, (ComparisonOperator,), {"expression": expression}),
    )


Eq = create_operator(name="Eq", mongo_operator="$eq")
Ne = create_operator(name="Ne", mongo_operator="$ne")
Gt = create_operator(name="Gt", mongo_operator="$gt")
Gte = create_operator(name="Gte", mongo_operator="$gte")
Lt = create_operator(name="Lt", mongo_operator="$lt")
Lte = create_operator(name="Lte", mongo_operator="$lte")
In = create_operator(name="In", mongo_operator="$in")
Nin = create_operator(name="Nin", mongo_operator="$nin")


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

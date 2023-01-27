from __future__ import annotations

import abc
from typing import Any, Optional, Type, TypeVar, Union, cast

from ..base import Expression


class EmptyType:
    def __repr__(self) -> str:
        return "EmptyType"

    def __copy__(self) -> EmptyType:
        return self

    def __reduce__(self) -> str:
        return "EmptyType"

    def __deepcopy__(self, _: Any) -> EmptyType:
        return self


Empty = EmptyType()


class Wrapped:
    def __init__(self, value: Optional[Any] = None):
        self.value = value

    def unwrap(self) -> Any:
        return self.value


class OptionalWrapped(Wrapped):
    def __init__(self, value: Optional[Any] = None):
        super().__init__(value=value)

    def unwrap(self) -> Union[Empty, Any]:
        return self.value if self.value is not None else Empty


WrappedType = TypeVar("WrappedType", bound=Wrapped)


class ComparisonOperator(Expression):
    def __init__(self, field: str, value: WrappedType):
        self.field = field
        self.value = value.unwrap()

    def expression(self) -> dict[str, Any]:
        return self.get_expression() if self.value is not Empty else {}

    @abc.abstractmethod
    def get_expression(self) -> dict[str, Any]:
        raise NotImplementedError


def create_operator(name: str, mongo_operator: str) -> Type[ComparisonOperator]:
    def get_expression(self) -> dict[str, Any]:
        return {self.field: {mongo_operator: self.value}}

    return cast(
        Type[ComparisonOperator],
        type(name, (ComparisonOperator,), {"get_expression": get_expression}),
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
        value: OptionalWrapped,
        options: str = "ms",
    ):
        super().__init__(field=field, value=value)
        self.options = options

    def get_expression(self) -> dict[str, Any]:
        return {self.field: {"$regex": self.value, "$options": self.options}}

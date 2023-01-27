import abc
from typing import Any, Optional, Type, cast

from ..base import Expression


class ComparisonOperator(Expression):
    def __init__(self, field: str, value: Optional[Any] = None, compare_none: bool = False):
        self.field = field
        self.value = value
        self.compare_none = compare_none

    def expression(self) -> dict[str, Any]:
        if self.value is None and not self.compare_none:
            return {}
        return self.get_expression()

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
In = create_operator("In", mongo_operator="$in")
Nin = create_operator("Nin", mongo_operator="$nin")


class Regex(ComparisonOperator):
    def __init__(
        self,
        field: str,
        value: Optional[str] = None,
        options: str = "ms",
    ):
        super().__init__(field=field, value=value, compare_none=False)
        self.options = options

    def get_expression(self) -> dict[str, Any]:
        return {self.field: {"$regex": self.value, "$options": self.options}}

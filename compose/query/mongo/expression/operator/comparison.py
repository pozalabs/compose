import abc
from typing import Any, Optional

from ..base import Expression


class ComparisonOperator(Expression):
    def __init__(self, field: str, value: Optional[Any] = None, compare_none: bool = False):
        self.field = field
        self.value = value
        self.compare_none = compare_none

    def expression(self) -> dict[str, Any]:
        if self.value is None and self.compare_none:
            return {}
        return self.get_expression()

    @abc.abstractmethod
    def get_expression(self) -> dict[str, Any]:
        raise NotImplementedError


class Equal(ComparisonOperator):
    def __init__(self, field: str, value: Optional[Any] = None, compare_none: bool = False):
        super().__init__(field=field, value=value, compare_none=compare_none)

    def get_expression(self) -> dict[str, Any]:
        return {self.field: self.value}


class In(ComparisonOperator):
    def __init__(self, field: str, value: Optional[list[Any]] = None):
        super().__init__(field=field, value=value, compare_none=False)

    def get_expression(self) -> dict[str, Any]:
        return {self.field: {"$in": self.value}}


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


class Gte(ComparisonOperator):
    def __init__(self, field: str, value: Optional[int] = None):
        super().__init__(field=field, value=value, compare_none=False)

    def get_expression(self) -> dict[str, Any]:
        return {self.field: {"$gte": self.value}}


class Lt(ComparisonOperator):
    def __init__(self, field: str, value: Optional[int] = None):
        super().__init__(field=field, value=value, compare_none=False)

    def get_expression(self) -> dict[str, Any]:
        return {self.field: {"$lt": self.value}}

import abc
from typing import Any

from .base import Expression


class Operator(Expression):
    def __init__(self, field: str, value: Any, compare_none: bool = False):
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

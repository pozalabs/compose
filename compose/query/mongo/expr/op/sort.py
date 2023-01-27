from typing import Any

from ..base import Expression


class SortBy(Expression):
    def __init__(self, field: str, direction: int):
        self.field = field
        self.direction = direction

    def expression(self) -> dict[str, Any]:
        return {self.field: self.direction}

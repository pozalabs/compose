from .base import Operator


class SortBy(Operator):
    def __init__(self, field: str, direction: int):
        self.field = field
        self.direction = direction

    def expression(self) -> dict[str, int]:
        return {self.field: self.direction}

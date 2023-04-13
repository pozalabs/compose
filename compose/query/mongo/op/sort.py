from __future__ import annotations

import pymongo

from .base import Operator


class SortBy(Operator):
    def __init__(self, field: str, direction: int):
        self.field = field
        self.direction = direction

    def expression(self) -> dict[str, int]:
        return {self.field: self.direction}

    @classmethod
    def asc(cls, field: str) -> SortBy:
        return cls(field=field, direction=pymongo.ASCENDING)

    @classmethod
    def desc(cls, field: str) -> SortBy:
        return cls(field=field, direction=pymongo.DESCENDING)

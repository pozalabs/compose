from __future__ import annotations

from typing import Literal

import pymongo

from .base import Operator
from .types import DictExpression


class SortBy(Operator):
    def __init__(self, field: str, direction: Literal[1, -1]):
        self.field = field
        self.direction = direction

    def expression(self) -> DictExpression:
        return {self.field: self.direction}

    @classmethod
    def asc(cls, field: str) -> SortBy:
        return cls(field=field, direction=pymongo.ASCENDING)

    @classmethod
    def desc(cls, field: str) -> SortBy:
        return cls(field=field, direction=pymongo.DESCENDING)

    @classmethod
    def from_(cls, key: str) -> SortBy:
        if key.startswith("-"):
            return cls.desc(field=key[1:])
        return cls.asc(field=key)

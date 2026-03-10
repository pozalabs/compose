from __future__ import annotations

from typing import Any, TypeVar

DictExpression = dict[str, Any]
ListExpression = list[DictExpression]
Expression = TypeVar("Expression", DictExpression, ListExpression)

Id = "$_id"


class _FieldPath(str):
    def __new__(cls, v: str):
        if not v.startswith("$"):
            raise ValueError("path must be prefixed with $")

        return super().__new__(cls, v)


class _String(str):
    def __new__(cls, v: str):
        if v.startswith("$"):
            raise ValueError("string must not be prefixed with $")

        return super().__new__(cls, v)


class _NonNegativeInt(int):
    def __new__(cls, v: int):
        if v < 0:
            raise ValueError(f"Expected non-negative integer, got {v}")
        return super().__new__(cls, v)


class _PositiveInt(int):
    def __new__(cls, v: int):
        if v <= 0:
            raise ValueError(f"Expected positive integer, got {v}")
        return super().__new__(cls, v)

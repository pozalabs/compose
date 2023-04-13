from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import inflection

DictExpression = dict[str, Any]
ListExpression = list[DictExpression]


class MongoKeyword(str):
    def __new__(cls, v: str):
        if v != _camelize(v):
            raise ValueError(f"Cannot interpret {v} as valid mongo keyword")

        return super().__new__(cls, v)

    @classmethod
    def from_py(cls, v: str) -> MongoKeyword:
        return cls(_camelize(v))


def _camelize(v: str) -> str:
    return inflection.camelize(v.strip("_"), uppercase_first_letter=False)


@runtime_checkable
class Expressionable(Protocol):
    def expression(self) -> Any:
        ...


class Input:
    def __init__(self, value: Any):
        self.value = value

    def unwrap(self) -> Any:
        return self.value.expression() if isinstance(self.value, Expressionable) else self.value

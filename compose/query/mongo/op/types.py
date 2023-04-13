from __future__ import annotations

from typing import Any, ClassVar, Union

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


class AggVar(str):
    prefix: ClassVar[str] = "$"

    def __new__(cls, v: Union[str, AggVar]):
        num_prefixes = v.count(cls.prefix)
        if num_prefixes > 2:
            raise ValueError(f"Cannot interpret {v} as valid aggregation variable")

        if not v.startswith(cls.prefix):
            v = f"{cls.prefix * 2}{v}"

        return super().__new__(cls, v)

    @classmethod
    def current(cls, value: str) -> AggVar:
        return AggVar(f"{cls.prefix}{value}")

    @classmethod
    def root(cls) -> AggVar:
        return cls.current("ROOT")

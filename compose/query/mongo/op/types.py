from __future__ import annotations

import copy
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
    """https://www.mongodb.com/docs/manual/reference/aggregation-variables/"""

    prefix: ClassVar[str] = "$"

    def __new__(cls, v: Union[str, AggVar]):
        copied = copy.deepcopy(v)
        num_prefixes = 0
        prefix_removed = not v.startswith(cls.prefix)
        while not prefix_removed:
            copied = copied[1:]
            num_prefixes += 1
            prefix_removed = not copied.startswith(cls.prefix)

        if num_prefixes not in (1, 2):
            raise ValueError(f"Cannot interpret {v} as valid aggregation variable")

        return super().__new__(cls, v)

    @classmethod
    def from_(cls, v: str) -> AggVar:
        if v.startswith(cls.prefix):
            raise ValueError(f"`v` must not start with `{cls.prefix}`")

        return cls(f"{cls.prefix * 2}{v}")

    @classmethod
    def current(cls, v: str) -> AggVar:
        if v.startswith(cls.prefix):
            raise ValueError(f"`v` must not start with `{cls.prefix}`")

        return AggVar(f"{cls.prefix}{v}")

    @classmethod
    def root(cls) -> AggVar:
        return cls.current("ROOT")

from __future__ import annotations

from typing import Any

import inflection

DictExpression = dict[str, Any]
ListExpression = list[DictExpression]


class MongoKeyword(str):
    @classmethod
    def from_py(cls, v: str) -> MongoKeyword:
        return cls(inflection.camelize(v.strip("_"), uppercase_first_letter=False))

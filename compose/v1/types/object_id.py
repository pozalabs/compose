from __future__ import annotations

from collections.abc import Callable, Generator
from typing import Any

import bson


class PyObjectId(bson.ObjectId):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], bson.ObjectId], None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v: bson.ObjectId | bytes) -> bson.ObjectId:
        if not bson.ObjectId.is_valid(v):
            raise ValueError("Invalid object id")
        return bson.ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema: dict[str, Any]) -> None:
        field_schema.update(type="string")

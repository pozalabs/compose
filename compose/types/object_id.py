from __future__ import annotations

from collections.abc import Callable
from typing import Any, Type, Union

import bson
from pydantic_core import CoreSchema, core_schema


class PyObjectId(bson.ObjectId):
    @classmethod
    def validate(
        cls, v: Union[bson.ObjectId, bytes], _: core_schema.ValidationInfo
    ) -> bson.ObjectId:
        if not bson.ObjectId.is_valid(v):
            raise ValueError("Invalid object id")
        return bson.ObjectId(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Type[PyObjectId]) -> CoreSchema:
        return core_schema.general_plain_validator_function(
            cls.validate, serialization=core_schema.to_string_ser_schema()
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        schema: core_schema.CoreSchema,
        handler: Callable[[Any], core_schema.CoreSchema],
    ) -> CoreSchema:
        return dict(type="string")

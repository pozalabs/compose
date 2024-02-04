from collections.abc import Callable, Generator
from typing import Any, Self

import bson

from .. import compat

if compat.IS_PYDANTIC_V2:
    from pydantic_core import CoreSchema, core_schema


class PyObjectId(bson.ObjectId):
    if compat.IS_PYDANTIC_V2:

        @classmethod
        def validate(
            cls, v: bson.ObjectId | bytes, _: core_schema.ValidationInfo = None
        ) -> bson.ObjectId:
            return cls._validate(v)

        @classmethod
        def __get_pydantic_core_schema__(cls, source_type: type[Self]) -> CoreSchema:
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

    else:

        @classmethod
        def __get_validators__(cls) -> Generator[Callable[[Any], bson.ObjectId], None, None]:
            yield cls.validate

        @classmethod
        def validate(cls, v: bson.ObjectId | bytes) -> bson.ObjectId:
            return cls._validate(v)

        @classmethod
        def __modify_schema__(cls, field_schema: dict[str, Any]) -> None:
            field_schema.update(type="string")

    @classmethod
    def _validate(cls, v: bson.ObjectId | bytes) -> bson.ObjectId:
        if not bson.ObjectId.is_valid(v):
            raise ValueError("Invalid object id")
        return bson.ObjectId(v)

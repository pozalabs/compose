from typing import Any

import pytest

import compose

if not compose.compat.IS_PYDANTIC_V2:
    pytest.skip("pydantic v2 only", allow_module_level=True)
else:
    from pydantic import GetCoreSchemaHandler, TypeAdapter
    from pydantic.v1.validators import str_validator
    from pydantic_core import core_schema


class StrippedStr(str):
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        return v.strip()

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return compose.types.get_pydantic_core_schema(cls, handler(str))


def test_get_pydantic_core_schema():
    validated_type = TypeAdapter(StrippedStr).validate_python(" test ")

    assert validated_type == StrippedStr("test")

from typing import Any

import pytest
from pydantic import GetCoreSchemaHandler, TypeAdapter
from pydantic_core import core_schema

from compose import compat

if compat.IS_PYDANTIC_V2:
    from pydantic.v1.validators import str_validator

    from compose.types import get_pydantic_core_schema


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
        return get_pydantic_core_schema(cls, handler(str))


@pytest.mark.skipif(not compat.IS_PYDANTIC_V2)
def test_get_pydantic_core_schema():
    validated_type = TypeAdapter(StrippedStr).validate_python(" test ")

    assert validated_type == StrippedStr("test")

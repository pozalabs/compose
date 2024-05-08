import pytest

import compose

if not compose.compat.IS_PYDANTIC_V2:
    pytest.skip("pydantic v2 only", allow_module_level=True)
else:
    from pydantic import TypeAdapter
    from pydantic.v1.validators import str_validator


class StrippedStr(str, compose.types.CoreSchemaGettable):
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        return v.strip()


def test_get_pydantic_core_schema():
    validated_type = TypeAdapter(StrippedStr).validate_python(" test ")

    assert validated_type == StrippedStr("test")

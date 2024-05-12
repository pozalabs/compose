import pytest

import compose

if compose.compat.IS_PYDANTIC_V2:
    from pydantic import TypeAdapter
    from pydantic.v1.validators import str_validator
else:
    from pydantic import parse_obj_as
    from pydantic.validators import str_validator


class LowerStr(str, compose.types.CoreSchemaGettable[str]):
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        return v.lower()


@pytest.mark.skipif(not compose.compat.IS_PYDANTIC_V2, reason="pydantic v2 only")
@pytest.mark.parametrize(
    "value, expected",
    [
        ("TEST", LowerStr("test")),
        ("Test", LowerStr("test")),
    ],
)
def test_get_pydantic_core_schema(value: str, expected: LowerStr):
    assert TypeAdapter(LowerStr).validate_python(value) == expected


@pytest.mark.skipif(compose.compat.IS_PYDANTIC_V2, reason="pydantic v1 only")
@pytest.mark.parametrize(
    "value, expected",
    [
        ("TEST", LowerStr("test")),
        ("Test", LowerStr("test")),
    ],
)
def test_get_pydantic_core_schema_v1(value: str, expected: LowerStr):
    assert parse_obj_as(LowerStr, value) == expected

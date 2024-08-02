import pytest
from pydantic import TypeAdapter
from pydantic.v1.validators import str_validator

import compose


class LowerStr(str, compose.types.CoreSchemaGettable[str]):
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        return v.lower()


@pytest.mark.parametrize(
    "value, expected",
    [
        ("TEST", LowerStr("test")),
        ("Test", LowerStr("test")),
    ],
)
def test_get_pydantic_core_schema(value: str, expected: LowerStr):
    assert TypeAdapter(LowerStr).validate_python(value) == expected

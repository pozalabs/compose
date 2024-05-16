import pytest

import compose


class LowerStr(str, compose.types.CoreSchemaGettable[str]):
    @classmethod
    def __get_validators__(cls):
        yield compose.compat.str_validator
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
    assert compose.compat.validate_obj(LowerStr, value) == expected

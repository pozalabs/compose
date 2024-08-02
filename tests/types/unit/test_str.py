import pytest
from pydantic import TypeAdapter, ValidationError

import compose


class CustomType(compose.types.Str): ...


def test_str():
    assert TypeAdapter(CustomType).validate_python("test") == CustomType("test")


def test_str_invalid():
    with pytest.raises(ValidationError):
        TypeAdapter(CustomType).validate_python(123)

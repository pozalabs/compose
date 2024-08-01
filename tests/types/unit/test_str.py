import pytest
from pydantic import ValidationError

import compose


class CustomType(compose.types.Str): ...


def test_str():
    assert compose.compat.validate_obj(CustomType, "test") == CustomType("test")


def test_str_invalid():
    with pytest.raises(ValidationError):
        compose.compat.validate_obj(CustomType, 123)

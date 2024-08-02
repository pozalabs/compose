from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

import compose


class CustomType(compose.types.StrList): ...


def test_str_list():
    assert TypeAdapter(CustomType).validate_python(["1", "2", "3"]) == CustomType(["1", "2", "3"])


@pytest.mark.parametrize(
    "value",
    [[1, 2, 3], [1.1, 2.2, 3.3], "test"],
)
def test_str_list_invalid(value: Any):
    with pytest.raises(ValidationError):
        TypeAdapter(CustomType).validate_python(value)

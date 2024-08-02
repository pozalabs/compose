from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

import compose


class CustomType(compose.types.IntList): ...


@pytest.mark.parametrize(
    "value",
    [
        [1, 2, 3],
        [1.0, 2.0, 3.0],
    ],
)
def test_int_list(value: Any):
    assert TypeAdapter(CustomType).validate_python(value) == CustomType([1, 2, 3])


def test_int_list_invalid():
    with pytest.raises(ValidationError):
        TypeAdapter(CustomType).validate_python("test")

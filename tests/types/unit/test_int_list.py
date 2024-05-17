from typing import Any

import pytest
from pydantic import ValidationError

import compose


class CustomType(compose.types.IntList):
    ...


@pytest.mark.parametrize(
    "value",
    [
        [1, 2, 3],
        [1.0, 2.0, 3.0],
    ],
)
def test_int_list(value: Any):
    assert compose.compat.validate_obj(CustomType, value) == CustomType([1, 2, 3])


def test_int_list_invalid():
    with pytest.raises(ValidationError):
        compose.compat.validate_obj(CustomType, "test")

from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

import compose


class CustomStrList(compose.types.List[str]): ...


class CustomIntList(compose.types.List[int]): ...


def test_list_str_valid():
    assert TypeAdapter(CustomStrList).validate_python(["1", "2", "3"]) == CustomStrList(
        ["1", "2", "3"]
    )


def test_list_int_valid():
    assert TypeAdapter(CustomIntList).validate_python([1, 2, 3]) == CustomIntList([1, 2, 3])
    assert TypeAdapter(CustomIntList).validate_python([1.0, 2.0, 3.0]) == CustomIntList([1, 2, 3])


@pytest.mark.parametrize(
    "value",
    [[1, 2, 3], [1.1, 2.2, 3.3], "test", 123],
)
def test_list_str_invalid(value: Any):
    with pytest.raises(ValidationError):
        TypeAdapter(CustomStrList).validate_python(value)


def test_list_int_invalid():
    with pytest.raises(ValidationError):
        TypeAdapter(CustomIntList).validate_python("test")


def test_list_caching():
    type1 = compose.types.List[str]
    type2 = compose.types.List[str]

    assert type1 is type2

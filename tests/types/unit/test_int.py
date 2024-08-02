from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

import compose


class CustomType(compose.types.Int): ...


@pytest.mark.parametrize(
    "value",
    [123, "123"],
    ids=(
        "값이 상속하는 타입과 동일한 타입인 경우 유효한 값이다.",
        "값이 상속하는 타입과 다른 타입이더라도 타입 캐스팅이 가능한 타입이면 유효한 값이다.",
    ),
)
def test_int(value: Any):
    assert TypeAdapter(CustomType).validate_python(value) == CustomType(value)


def test_int_invalid():
    with pytest.raises(ValidationError):
        TypeAdapter(CustomType).validate_python([1, 2, 3])

from typing import Any

import pytest
from pydantic import ValidationError

import compose


class CustomType(compose.types.Float):
    ...


@pytest.mark.parametrize(
    "value",
    [1.23, "1.23"],
    ids=(
        "값이 상속하는 타입과 동일한 타입인 경우 유효한 값이다.",
        "값이 상속하는 타입과 다른 타입이더라도 타입 캐스팅이 가능한 타입이면 유효한 값이다.",
    ),
)
def test_float(value: Any):
    assert compose.compat.validate_obj(CustomType, value) == CustomType(value)


def test_float_invalid():
    with pytest.raises(ValidationError):
        compose.compat.validate_obj(CustomType, [1, 2, 3])

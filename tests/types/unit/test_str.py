from typing import Any

import pytest
from pydantic import ValidationError

import compose


class CustomType(compose.types.Str):
    pass


@pytest.mark.skipif(not compose.compat.IS_PYDANTIC_V2, reason="pydantic v2 only")
def test_str():
    assert compose.compat.validate_obj(CustomType, "test") == CustomType("test")


@pytest.mark.skipif(not compose.compat.IS_PYDANTIC_V2, reason="pydantic v2 only")
def test_str_invalid():
    with pytest.raises(ValidationError):
        compose.compat.validate_obj(CustomType, 123)


@pytest.mark.skipif(compose.compat.IS_PYDANTIC_V2, reason="pydantic v1 only")
@pytest.mark.parametrize(
    "value",
    [("test"), (123)],
    ids=(
        "값이 상속하는 타입과 동일한 타입인 경우 유효한 값이다.",
        "v1에서는 값이 상속하는 타입과 다른 타입이더라도 타입 캐스팅이 가능한 타입이면 유효한 값이다.",
    ),
)
def test_str_v1(value: Any):
    assert compose.compat.validate_obj(CustomType, value) == CustomType(value)


@pytest.mark.skipif(compose.compat.IS_PYDANTIC_V2, reason="pydantic v1 only")
def test_str_v1_invalid():
    with pytest.raises(ValidationError):
        compose.compat.validate_obj(CustomType, [1, 2, 3])

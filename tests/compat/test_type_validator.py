from collections.abc import Callable, Generator
from typing import Any, Self

import pytest

import compose

if compose.compat.IS_PYDANTIC_V2:
    from pydantic import TypeAdapter
else:
    from pydantic import parse_obj_as


class SomeStr(str, compose.types.CoreSchemaGettable[str]):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], Self], None, None]:
        yield compose.compat.str_validator
        yield lambda v: cls(v)


@pytest.mark.skipif(not compose.compat.IS_PYDANTIC_V2, reason="pydantic v2 only")
def test_str_validator():
    assert TypeAdapter(SomeStr).validate_python("test") == SomeStr("test")


@pytest.mark.skipif(compose.compat.IS_PYDANTIC_V2, reason="pydantic v1 only")
def test_str_validator_v1():
    assert parse_obj_as(SomeStr, "test") == SomeStr("test")

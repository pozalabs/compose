from collections.abc import Callable, Generator
from typing import Any, Self

import compose


class SomeStr(str, compose.types.CoreSchemaGettable[str]):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], Self], None, None]:
        yield compose.compat.str_validator
        yield lambda v: cls(v)


def test_str_validator():
    assert compose.compat.validate_obj(SomeStr, "test") == SomeStr("test")

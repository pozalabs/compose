from collections.abc import Callable, Generator
from typing import Any, Self, TypeVar

from compose import compat

from . import CoreSchemaGettable

T = TypeVar("T")


def caster(factory: Callable[[Any], T], /) -> Callable[[Any], T]:
    def _cast(v: Any) -> T:
        return factory(v)

    return _cast


class Str(str, CoreSchemaGettable[str]):
    @classmethod
    def __get_validators__(cls) -> Generator[[Callable[[Any], Self]], None, None]:
        yield compat.str_validator
        yield caster(cls)


class Int(int, CoreSchemaGettable[int]):
    @classmethod
    def __get_validators__(cls) -> Generator[[Callable[[Any], Self]], None, None]:
        yield compat.int_validator
        yield caster(cls)

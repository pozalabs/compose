import types
from collections.abc import Callable, Generator
from typing import Any, Self, TypeVar, cast

from compose import compat

from .helper import CoreSchemaGettable

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


class Float(float, CoreSchemaGettable[float]):
    @classmethod
    def __get_validators__(cls) -> Generator[[Callable[[Any], Self]], None, None]:
        yield compat.float_validator
        yield caster(cls)


class StrList(list[str], CoreSchemaGettable[list[str]]):
    @classmethod
    def __get_validators__(cls) -> Generator[[Callable[[Any], Self]], None, None]:
        yield compat.list_validator
        yield caster(cls)


class IntList(list[int], CoreSchemaGettable[list[int]]):
    @classmethod
    def __get_validators__(cls) -> Generator[[Callable[[Any], Self]], None, None]:
        yield compat.list_validator
        yield caster(cls)


def _create_list_type(t: T, /) -> type[list[T]]:
    def __get_validators__(c):
        yield compat.list_validator
        yield caster(c)

    return cast(
        type[list[T]],
        types.new_class(
            f"{t.__name__.title()}List",
            (list[t], CoreSchemaGettable[list[t]]),
            exec_body=lambda ns: ns.update(
                {
                    "__get_validators__": classmethod(__get_validators__),
                }
            ),
        ),
    )


def create_list_type() -> Callable[[[T]], type[list[T]]]:
    cache = {}

    def factory(t: T) -> type[list[T]]:
        type_name = t.__name__

        if (cached := cache.get(type_name)) is not None:
            return cached

        _result = _create_list_type(t)
        cache[type_name] = _result
        return _result

    return factory


TypedList = create_list_type()

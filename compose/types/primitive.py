import types
from collections.abc import Callable
from typing import Any, cast

from compose import typing

from .helper import CoreSchemaGettable


def caster[T](factory: Callable[[Any], T], /) -> Callable[[Any], T]:
    def _cast(v: Any) -> T:
        return factory(v)

    return _cast


class Str(str, CoreSchemaGettable[str]):
    @classmethod
    def __get_validators__(cls) -> typing.ValidatorGenerator:
        yield caster(cls)


class Int(int, CoreSchemaGettable[int]):
    @classmethod
    def __get_validators__(cls) -> typing.ValidatorGenerator:
        yield caster(cls)


class Float(float, CoreSchemaGettable[float]):
    @classmethod
    def __get_validators__(cls) -> typing.ValidatorGenerator:
        yield caster(cls)


def _create_list_type[T](t: type[T], /) -> type[list[T]]:
    def __get_validators__(c) -> typing.ValidatorGenerator:
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


def create_list_type[T]() -> Callable[[type[T]], type[list[T]]]:
    cache = {}

    def factory(t: type[T]) -> type[list[T]]:
        type_name = t.__name__

        if (cached := cache.get(type_name)) is not None:
            return cached

        _result = _create_list_type(t)
        cache[type_name] = _result
        return _result

    return factory


TypedList = create_list_type()
StrList = TypedList(str)
IntList = TypedList(int)

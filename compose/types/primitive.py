from collections.abc import Callable
from typing import Any, Self

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

MARKER_IS_COMPOSE_VALIDATOR = "_is_compose_validator"


def validator(func: Callable[..., Any]) -> Callable[..., Any]:
    setattr(func, MARKER_IS_COMPOSE_VALIDATOR, True)
    return func


def _is_compose_validator(obj: Any) -> bool:
    return isinstance(obj, classmethod) and getattr(obj, MARKER_IS_COMPOSE_VALIDATOR, False)


def _get_pydantic_core_schema(
    validated_type: Any, schema: core_schema.CoreSchema
) -> core_schema.CoreSchema:
    return core_schema.no_info_after_validator_function(validated_type, schema)


class Str(str):
    _validators: list = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._validators = [
            member.__func__
            for klass in reversed(cls.__mro__)
            for member in klass.__dict__.values()
            if _is_compose_validator(member)
        ]

    @classmethod
    def validated(cls, v, /) -> Self:
        for func in cls._validators:
            v = func(cls, v)
        return cls(v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return _get_pydantic_core_schema(source_type.validated, handler(str))


class Int(int):
    _validators: list = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._validators = [
            member.__func__
            for klass in reversed(cls.__mro__)
            for member in klass.__dict__.values()
            if _is_compose_validator(member)
        ]

    @classmethod
    def validated(cls, v, /) -> Self:
        for func in cls._validators:
            v = func(cls, v)
        return cls(v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return _get_pydantic_core_schema(source_type.validated, handler(int))


class Float(float):
    _validators: list = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._validators = [
            member.__func__
            for klass in reversed(cls.__mro__)
            for member in klass.__dict__.values()
            if _is_compose_validator(member)
        ]

    @classmethod
    def validated(cls, v, /) -> Self:
        for func in cls._validators:
            v = func(cls, v)
        return cls(v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return _get_pydantic_core_schema(source_type.validated, handler(float))


class ListMeta(type):
    _cache: dict[str, type] = {}

    def __getitem__(cls, item):
        type_name = item.__name__ if hasattr(item, "__name__") else str(item)
        if (cached := cls._cache.get(type_name)) is not None:
            return cached

        element_type = item
        new_cls = type(
            f"{type_name.title()}List",
            (list,),
            {
                "__get_pydantic_core_schema__": classmethod(
                    lambda c, source_type, handler, _et=element_type: _get_pydantic_core_schema(
                        source_type, handler(list[_et])
                    )
                )
            },
        )
        cls._cache[type_name] = new_cls
        return new_cls


class List(list, metaclass=ListMeta): ...

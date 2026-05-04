from typing import Any, Self

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


def validator(fn):
    fn._is_validator = True
    return fn


class Str(str):
    _validators: list = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._validators = [
            member.__func__
            for klass in reversed(cls.__mro__)
            for member in klass.__dict__.values()
            if isinstance(member, classmethod) and getattr(member.__func__, "_is_validator", False)
        ]

    @classmethod
    def validated(cls, v, /) -> Self:
        for fn in cls._validators:
            v = fn(cls, v)
        return cls(v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(source_type.validated, handler(str))


class Int(int):
    _validators: list = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._validators = [
            member.__func__
            for klass in reversed(cls.__mro__)
            for member in klass.__dict__.values()
            if isinstance(member, classmethod) and getattr(member.__func__, "_is_validator", False)
        ]

    @classmethod
    def validated(cls, v, /) -> Self:
        for fn in cls._validators:
            v = fn(cls, v)
        return cls(v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(source_type.validated, handler(int))


class Float(float):
    _validators: list = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._validators = [
            member.__func__
            for klass in reversed(cls.__mro__)
            for member in klass.__dict__.values()
            if isinstance(member, classmethod) and getattr(member.__func__, "_is_validator", False)
        ]

    @classmethod
    def validated(cls, v, /) -> Self:
        for fn in cls._validators:
            v = fn(cls, v)
        return cls(v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(source_type.validated, handler(float))


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
                    lambda c, source_type, handler, _et=element_type: (
                        core_schema.no_info_after_validator_function(
                            source_type, handler(list[_et])
                        )
                    )
                )
            },
        )
        cls._cache[type_name] = new_cls
        return new_cls


class List(list, metaclass=ListMeta): ...

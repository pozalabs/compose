from collections.abc import Callable
from typing import TYPE_CHECKING, Any, ClassVar, Self, get_args

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

type Validators = list[Callable[..., Any]]

MARKER_IS_COMPOSE_VALIDATOR = "_is_compose_validator"


def validator(func: Callable[..., Any]) -> Callable[..., Any]:
    setattr(func, MARKER_IS_COMPOSE_VALIDATOR, True)
    return func


def _is_compose_validator(obj: Any) -> bool:
    return isinstance(obj, classmethod) and getattr(
        obj.__func__, MARKER_IS_COMPOSE_VALIDATOR, False
    )


def _get_pydantic_core_schema(
    validated_type: Any, schema: core_schema.CoreSchema
) -> core_schema.CoreSchema:
    return core_schema.no_info_after_validator_function(validated_type, schema)


class Str(str):
    if TYPE_CHECKING:
        _validators: ClassVar[Validators]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._validators = [
            member.__func__
            for type_ in reversed(cls.__mro__)
            for member in type_.__dict__.values()
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
    if TYPE_CHECKING:
        _validators: ClassVar[Validators]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._validators = [
            member.__func__
            for type_ in reversed(cls.__mro__)
            for member in type_.__dict__.values()
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
    if TYPE_CHECKING:
        _validators: ClassVar[Validators]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._validators = [
            member.__func__
            for type_ in reversed(cls.__mro__)
            for member in type_.__dict__.values()
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


class List[T](list[T]):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        args = get_args(source_type)
        if not args:
            for base in getattr(source_type, "__orig_bases__", ()):
                args = get_args(base)
                if args:
                    break
        if args:
            return _get_pydantic_core_schema(source_type, handler(list[args[0]]))
        return _get_pydantic_core_schema(source_type, handler(list))

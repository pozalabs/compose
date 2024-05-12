import copy
from collections.abc import Callable, Generator
from typing import Any, Generic, Protocol, TypeVar, get_args

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

T = TypeVar("T")


class SupportsGetValidators(Protocol):
    """Naming Convention: https://github.com/python/typeshed/issues/4174"""

    @classmethod
    def __get_validators__(cls) -> Generator[[Callable[[Any], Any]], None, None]:
        ...


def get_pydantic_core_schema(
    t: SupportsGetValidators, schema: core_schema.CoreSchema, /
) -> core_schema.CoreSchema:
    """Pydantic v1 커스텀 타입에 구현한 검증 제너레이터를 v2 커스텀 타입 검증 함수로 변환합니다.

    class CustomType(str):
        @classmethod
        def __get_validators__(cls):
            yield str_validator

        @classmethod
        def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: GetCoreSchemaHandler
        ) -> core_schema.CoreSchema:
            return compose.types.get_pydantic_core_schema(cls, handler(str))
    """

    if not hasattr(t, "__get_validators__"):
        raise AttributeError(f"{t.__class__.__name__} does not have `__get_validators__` method")

    return core_schema.no_info_after_validator_function(chain(*t.__get_validators__()), schema)


def chain(*validators: Callable[[Any], Any]) -> Callable[[Any], Any]:
    def apply_chain(v: Any) -> Any:
        result = copy.deepcopy(v)
        for validator in validators:
            result = validator(result)
        return result

    return apply_chain


class CoreSchemaGettable(Generic[T]):
    @classmethod
    def __get_pydantic_core_schema__(
        cls: SupportsGetValidators, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        validatable_type = get_args(source_type.__orig_bases__[0])[0]
        return get_pydantic_core_schema(cls, handler(validatable_type))


class _CoreSchemaGettableV1(Generic[T]):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> None:
        ...

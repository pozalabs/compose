from typing import Any, Generic, TypeVar

T = TypeVar("T")


class _DummyCoreSchemaGettable(Generic[T]):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> None:
        ...

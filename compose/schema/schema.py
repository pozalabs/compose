from collections.abc import Callable, Sequence
from typing import Any, Protocol, Self, get_args

from pydantic import ConfigDict

from .. import model
from ..pagination import CursorPaginationResult, OffsetPaginationResult
from .extra import schema_by_field_name


class Schema(model.BaseModel):
    model_config = ConfigDict(json_schema_extra=schema_by_field_name())


class Id[T](Schema):
    id: T


class TimeStampedSchema(model.TimeStampedModel, Schema): ...


class ListSchema[T](Schema):
    total: int
    items: list[T]

    @classmethod
    def from_result(
        cls,
        result: OffsetPaginationResult,
        parser: Callable[..., Any] | None = None,
    ) -> Self:
        if not result.items:
            return cls(**result.model_dump())

        annotation = cls.model_fields["items"].annotation
        item_type = get_args(annotation)[0]

        if not issubclass(item_type, model.BaseModel):
            data = result.model_dump(exclude={"extra"}) | result.extra
            return cls(**data)

        parser = parser or item_type.model_validate

        return cls(
            **result.model_dump(exclude={"items", "extra"}),
            **result.extra,
            items=[parser(item) for item in result.items],
        )

    @classmethod
    def from_items(cls, items: list[Any]) -> Self:
        return cls(total=len(items), items=items)


class CursorListSchema[T](Schema):
    items: list[T]
    next_cursor: str | None = None

    @classmethod
    def from_result(
        cls,
        result: CursorPaginationResult,
        parser: Callable[..., Any] | None = None,
    ) -> Self:
        if not result.items:
            return cls(items=[])

        annotation = cls.model_fields["items"].annotation
        item_type = get_args(annotation)[0]

        if not issubclass(item_type, model.BaseModel):
            return cls(**result.model_dump())

        parser = parser or item_type.model_validate

        return cls(
            items=[parser(item) for item in result.items],
            next_cursor=result.next_cursor,
        )


class InvalidParam(model.BaseModel):
    loc: str
    message: str
    type: str


class HasErrors(Protocol):
    def errors(self) -> Sequence[Any]: ...


class Error(model.BaseModel):
    title: str
    type: str
    detail: str | None = None
    invalid_params: list[InvalidParam] | None = None

    @classmethod
    def from_validation_error(cls, exc: HasErrors, title: str) -> Self:
        invalid_params = []
        for error in exc.errors():
            invalid_params.append(
                InvalidParam(
                    loc=".".join(str(v) for v in error["loc"]),
                    message=error["msg"],
                    type=error["type"],
                )
            )
        return cls(
            title=title,
            type="validation_error",
            invalid_params=invalid_params,
        )

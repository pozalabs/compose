from collections.abc import Sequence
from typing import Any, Protocol, Self, get_args

from pydantic import ConfigDict

from .. import container
from ..pagination import CursorPaginationResult, OffsetPaginationResult
from .extra import schema_by_field_name


class Schema(container.BaseModel):
    model_config = ConfigDict(json_schema_extra=schema_by_field_name())


class Id[T](Schema):
    id: T


class TimeStampedSchema(container.TimeStampedModel, Schema): ...


class ListSchema[T](Schema):
    total: int
    items: list[T]

    @classmethod
    def from_result(
        cls,
        result: OffsetPaginationResult,
        parser_name: str = "model_validate",
        **parser_kwargs: Any,
    ) -> Self:
        if not result.items:
            return cls(**result.model_dump())

        annotation = cls.model_fields["items"].annotation
        item_type = get_args(annotation)[0]

        if not issubclass(item_type, container.BaseModel):
            data = result.model_dump(exclude={"extra"}) | result.extra
            return cls(**data)

        if (parser := getattr(item_type, parser_name, None)) is None:
            raise AttributeError(f"{item_type.__name__} has no attribute: {parser_name}")

        return cls(
            **result.model_dump(exclude={"items", "extra"}),
            **result.extra,
            items=[parser(item, **parser_kwargs) for item in result.items],
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
        parser_name: str = "model_validate",
        **parser_kwargs: Any,
    ) -> Self:
        if not result.items:
            return cls(items=[])

        annotation = cls.model_fields["items"].annotation
        item_type = get_args(annotation)[0]

        if not issubclass(item_type, container.BaseModel):
            return cls(**result.model_dump())

        if (parser := getattr(item_type, parser_name, None)) is None:
            raise AttributeError(f"{item_type.__name__} has no attribute: {parser_name}")

        return cls(
            items=[parser(item, **parser_kwargs) for item in result.items],
            next_cursor=result.next_cursor,
        )


class InvalidParam(container.BaseModel):
    loc: str
    message: str
    type: str


class HasErrors(Protocol):
    def errors(self) -> Sequence[Any]: ...


class Error(container.BaseModel):
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

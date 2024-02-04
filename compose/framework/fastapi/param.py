from typing import TypeVar

from fastapi import Query
from fastapi._compat import field_annotation_is_scalar
from pydantic import BaseModel, Field, create_model

from compose import compat

Q = TypeVar("Q", bound=BaseModel)


def to_query(q: type[Q], /) -> type[Q]:
    field_args = (
        "title",
        "alias",
        "default",
        "default_factory",
        "description",
    )

    if compat.IS_PYDANTIC_V2:
        field_args = (*field_args, "annotation")
        field_definitions = {
            field_name: (
                field_info.annotation,
                (
                    field_info
                    if field_annotation_is_scalar(field_info.annotation)
                    else Field(Query(**{arg: getattr(field_info, arg, None) for arg in field_args}))
                ),
            )
            for field_name, field_info in q.model_fields.items()
        }
        return create_model(f"{q.__name__}Query", **field_definitions, __base__=q)

    else:
        field_definitions = {
            field_name: (
                field.outer_type_,
                (
                    field.field_info
                    if field_annotation_is_scalar(field.outer_type_)
                    else Field(Query(**{arg: getattr(field, arg, None) for arg in field_args}))
                ),
            )
            for field_name, field in q.__fields__.items()
        }

        class Child(q):
            class Config:
                arbitrary_types_allowed = True

        return create_model(
            f"{q.__name__}Query",
            **field_definitions,
            __base__=Child,
        )

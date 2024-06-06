import json
from typing import Any, TypeVar, get_args

from fastapi import Query
from fastapi._compat import field_annotation_is_scalar
from pydantic import BaseModel, Field, Json, create_model

from compose import compat

if compat.IS_PYDANTIC_V2:
    from pydantic import field_validator

Q = TypeVar("Q", bound=BaseModel)


def dict_to_json(cls_: type[Q], v: dict[str, Any] | None) -> str | None:
    if v is None:
        return v

    try:
        return json.dumps(v)
    except Exception as exc:
        raise ValueError(f"Invalid json: {exc}")


if compat.IS_PYDANTIC_V2:
    TYPE_VALIDATORS = {
        Json: [
            dict_to_json,
        ]
    }


def to_query(q: type[Q], /) -> type[Q]:
    field_args = (
        "title",
        "alias",
        "default",
        "default_factory",
        "description",
    )

    if compat.IS_PYDANTIC_V2:
        validators = {}
        field_args = (*field_args, "annotation")
        field_definitions = {}
        for field_name, field_info in q.model_fields.items():
            annotation = field_info.annotation
            field_definitions[field_name] = (
                annotation,
                Field(Query(**{arg: getattr(field_info, arg, None) for arg in field_args})),
            )
            if not (args := get_args(annotation)):
                continue

            if (arg := next((arg for arg in args if arg is not None), None)) is None:
                continue

            validators |= {
                f"{field_name}_{validator.__name__}": field_validator(field_name, mode="before")(
                    validator
                )
                for validator in TYPE_VALIDATORS.get(arg, [])
            }
            print(validators)

        return create_model(
            f"{q.__name__}Query",
            **field_definitions,
            __validators__=validators,
            __base__=q,
        )

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

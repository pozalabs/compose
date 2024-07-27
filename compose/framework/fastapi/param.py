from collections.abc import Callable
from typing import Annotated, Any, TypeVar, get_args

from fastapi import Depends, Query
from pydantic import BaseModel, Field, Json, create_model

from compose import compat, container

if compat.IS_PYDANTIC_V2:
    import pydantic_core
    from pydantic import field_validator

Q = TypeVar("Q", bound=BaseModel)
T = TypeVar("T", bound=container.BaseModel)


def dict_to_json(v: dict[str, Any] | None) -> str | None:
    if v is None:
        return v

    return pydantic_core.to_json(v).decode()


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
                Field(Query(**{arg: getattr(field, arg, None) for arg in field_args})),
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


def as_query(q: type[Q], /) -> type[Q]:
    return Annotated[q, Depends(to_query(q))]


def create_model_dependency_resolver(
    model_type: type[T],
    dependencies: dict[str, tuple[type, Any]],
) -> Callable[..., Any]:
    dependencies_model = create_model(
        f"{model_type.__name__}fields",
        **{
            name: (field_type, Field(field_value))
            for name, (field_type, field_value) in dependencies.items()
        },
    )

    def wrapper(
        t: model_type,
        resolved_dependencies: Annotated[dependencies_model, Depends(dependencies_model)],
    ) -> T:
        return t.copy(update=resolved_dependencies.dict(), deep=True)

    return wrapper


def with_depends(model_type: type[T], **params: Any) -> type[T]:
    return Annotated[
        model_type,
        Depends(create_model_dependency_resolver(model_type, params)),
    ]

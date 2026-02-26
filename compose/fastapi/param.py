import inspect
from collections.abc import Callable
from dataclasses import asdict
from typing import Annotated, Any, get_args

import pydantic_core
from fastapi import Depends, Path, Query, params
from pydantic import BaseModel, Field, Json, create_model, field_validator

from compose import query, types


def dict_to_json(v: dict[str, Any] | None) -> str | None:
    if v is None:
        return v

    return pydantic_core.to_json(v).decode()


TYPE_VALIDATORS = {
    Json: [
        dict_to_json,
    ]
}


def to_query[Q: BaseModel](q: type[Q], /) -> type[Q]:
    field_args = (
        "title",
        "alias",
        "default",
        "default_factory",
        "description",
    )

    validators = {}
    field_args = (*field_args, "annotation")
    field_definitions = {}
    for field_name, field_info in q.model_fields.items():
        annotation = field_info.annotation

        metadata = {}
        for item in field_info.metadata:
            metadata |= asdict(item)

        field_definitions[field_name] = (
            annotation,
            Field(
                Query(
                    **{arg: getattr(field_info, arg, None) for arg in field_args},
                    **metadata,
                )
            ),
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


def as_query[Q: BaseModel](q: type[Q], /) -> Any:
    return Depends(to_query(q))


def create_model_dependency_resolver[T: BaseModel](
    model_type: type[T],
    dependencies: dict[str, tuple[type, Any]],
) -> Callable[..., Any]:
    dep_names = list(dependencies.keys())

    def wrapper(t, **kwargs) -> T:
        return t.model_copy(update={name: kwargs[name] for name in dep_names}, deep=True)

    wrapper.__signature__ = inspect.Signature(
        parameters=[
            inspect.Parameter("t", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=model_type),
            *(
                inspect.Parameter(
                    name, inspect.Parameter.KEYWORD_ONLY, default=default, annotation=type_
                )
                for name, (type_, default) in dependencies.items()
            ),
        ],
    )
    return wrapper


def with_fields[T: BaseModel](model_type: type[T], **kwargs: Any) -> Any:
    return Depends(create_model_dependency_resolver(model_type, kwargs))


class FromPath:
    @classmethod
    def object_id(
        cls, path: params.Path | None = None
    ) -> "tuple[type[types.PyObjectId], params.Path]":
        if not hasattr(types, "PyObjectId"):
            raise ImportError("FromPath.object_id requires `bson`. Install `pymongo`")
        return types.PyObjectId, path or Path(...)

    @classmethod
    def int(cls, path: params.Path | None = None) -> tuple[type[int], params.Path]:
        return int, path or Path(...)

    @classmethod
    def str(cls, path: params.Path | None = None) -> tuple[type[str], params.Path]:
        return str, path or Path(...)


class FromAuth[U]:
    def __init__(self, user_getter: Callable[..., U]) -> None:
        self._user_getter = user_getter

    def field(self, attr: str, field_type: type) -> tuple[type, params.Depends]:
        user_getter = self._user_getter

        def get_field(user: U = Depends(user_getter)):
            return getattr(user, attr)

        return field_type, Depends(get_field)


class _OffsetPaginationParams(query.Query):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1)


OffsetPaginationParams = Annotated[_OffsetPaginationParams, as_query(_OffsetPaginationParams)]

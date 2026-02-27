import inspect
from collections.abc import Callable
from dataclasses import asdict
from typing import Annotated, Any, cast, get_args

import pydantic_core
from fastapi import Depends, Path, Query, params
from pydantic import BaseModel, Field, Json

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


_QUERY_FIELD_ARGS = ("title", "alias", "default", "default_factory", "description")


def _build_query_resolver[Q: BaseModel](q: type[Q], /) -> Callable[..., Q]:
    pre_validators: dict[str, list[Callable[..., Any]]] = {}
    for field_name, field_info in q.model_fields.items():
        for arg in get_args(field_info.annotation):
            for validator in TYPE_VALIDATORS.get(arg, []):
                pre_validators.setdefault(field_name, []).append(validator)

    def factory(**kwargs: Any) -> Q:
        for name, validators in pre_validators.items():
            if name in kwargs:
                for validator in validators:
                    kwargs[name] = validator(kwargs[name])
        return q(**kwargs)

    cast(Any, factory).__signature__ = inspect.Signature(
        parameters=[
            inspect.Parameter(
                field_name,
                inspect.Parameter.KEYWORD_ONLY,
                default=Query(
                    **{arg: getattr(field_info, arg, None) for arg in _QUERY_FIELD_ARGS},
                    **{k: v for item in field_info.metadata for k, v in asdict(item).items()},
                ),
                annotation=field_info.annotation,
            )
            for field_name, field_info in q.model_fields.items()
        ],
    )
    return factory


def as_query[Q: BaseModel](q: type[Q], /) -> Any:
    return Depends(_build_query_resolver(q))


def create_model_dependency_resolver[T: BaseModel](
    model_type: type[T],
    dependencies: dict[str, tuple[type, Any]],
) -> Callable[..., Any]:
    dep_names = list(dependencies.keys())

    def wrapper(t, **kwargs) -> T:
        return t.model_copy(update={name: kwargs[name] for name in dep_names}, deep=True)

    cast(Any, wrapper).__signature__ = inspect.Signature(
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

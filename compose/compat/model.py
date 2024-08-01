from typing import Any, TypeVar

from pydantic import BaseModel, TypeAdapter

T = TypeVar("T")


def validate_obj(t: type[T], value: Any, /) -> T:
    return TypeAdapter(t).validate_python(value)


def model_schema(t: type[BaseModel], **kwargs) -> dict[str, Any]:
    return t.model_json_schema(**kwargs)


def model_validate(t: type[BaseModel], obj: Any, **kwargs) -> BaseModel:
    return t.model_validate(obj, **kwargs)


def model_validate_json(t: type[BaseModel], obj: Any, **kwargs) -> BaseModel:
    return t.model_validate_json(obj, **kwargs)


def model_dump(t: BaseModel, **kwargs) -> dict[str, Any]:
    return t.model_dump(**kwargs)


def model_dump_json(t: BaseModel, **kwargs) -> str:
    return t.model_dump_json(**kwargs)

from typing import Any, TypeVar

import pydantic
from pydantic import BaseModel

IS_PYDANTIC_V2 = int(pydantic.VERSION.split(".")[0]) >= 2

if IS_PYDANTIC_V2:
    from pydantic import TypeAdapter
else:
    from pydantic import parse_obj_as

T = TypeVar("T")


def validate_obj(t: type[T], value: Any, /) -> T:
    if IS_PYDANTIC_V2:
        return TypeAdapter(t).validate_python(value)
    else:
        return parse_obj_as(t, value)


def model_schema(t: type[BaseModel], **kwargs) -> dict[str, Any]:
    if IS_PYDANTIC_V2:
        return t.model_json_schema(**kwargs)
    else:
        return t.schema(**kwargs)


def model_validate(t: type[BaseModel], obj: Any, **kwargs) -> BaseModel:
    if IS_PYDANTIC_V2:
        return t.model_validate(obj, **kwargs)
    else:
        return t.parse_obj(obj)


def model_dump(t: BaseModel, **kwargs) -> dict[str, Any]:
    if IS_PYDANTIC_V2:
        return t.model_dump(**kwargs)
    else:
        return t.dict(**kwargs)

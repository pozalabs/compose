from typing import Any, TypeVar

from pydantic import BaseModel

from . import utils

if utils.IS_PYDANTIC_V2:
    from pydantic import TypeAdapter
else:
    from pydantic import parse_obj_as

T = TypeVar("T")


def validate_obj(t: type[T], value: Any, /) -> T:
    if utils.IS_PYDANTIC_V2:
        return TypeAdapter(t).validate_python(value)
    else:
        return parse_obj_as(t, value)


def model_schema(t: type[BaseModel], **kwargs) -> dict[str, Any]:
    if utils.IS_PYDANTIC_V2:
        return t.model_json_schema(**kwargs)
    else:
        return t.schema(**kwargs)


def model_validate(t: type[BaseModel], obj: Any, **kwargs) -> BaseModel:
    if utils.IS_PYDANTIC_V2:
        return t.model_validate(obj, **kwargs)
    else:
        return t.parse_obj(obj, **kwargs)


def model_validate_json(t: type[BaseModel], obj: Any, **kwargs) -> BaseModel:
    if utils.IS_PYDANTIC_V2:
        return t.model_validate_json(obj, **kwargs)
    else:
        return t.parse_raw(obj, **kwargs)


def model_dump(t: BaseModel, **kwargs) -> dict[str, Any]:
    if utils.IS_PYDANTIC_V2:
        return t.model_dump(**kwargs)
    else:
        return t.dict(**kwargs)


def model_dump_json(t: BaseModel, **kwargs) -> str:
    if utils.IS_PYDANTIC_V2:
        return t.model_dump_json(**kwargs)
    else:
        return t.json(**kwargs)

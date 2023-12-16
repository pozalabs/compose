from typing import Any

from .. import compat
from .schema import Schema

try:
    import orjson
except ImportError:
    raise ImportError("Install `orjson` to use orjson schema")


def orjson_dumps(v: Any, *, default):
    return orjson.dumps(v, default=default).decode()


class ORJSONSchema(Schema):
    if not compat.IS_PYDANTIC_V2:

        class Config:
            json_loads = orjson.loads
            json_dumps = orjson_dumps

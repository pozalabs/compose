from typing import Any

from .schema import Schema

try:
    import orjson
except ImportError:
    raise ImportError("Install `orjson` to use orjson schema")


def orjson_dumps(v: Any, *, default):
    return orjson.dumps(v, default=default).decode()


class ORJSONSchema(Schema): ...

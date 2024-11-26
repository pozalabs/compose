from . import (
    auth,
    aws,
    command,
    concurrent,
    dependency,
    entity,
    enums,
    event,
    exceptions,
    field,
    handler,
    lock,
    messaging,
    pagination,
    query,
    repository,
    schema,
    settings,
    stream,
    types,
    typing,
    uow,
    utils,
)
from .container import BaseModel, TimeStampedModel

tp = typing

__all__ = [
    "BaseModel",
    "TimeStampedModel",
    "auth",
    "aws",
    "command",
    "concurrent",
    "dependency",
    "entity",
    "enums",
    "event",
    "exceptions",
    "fastapi",
    "field",
    "handler",
    "lock",
    "messaging",
    "pagination",
    "query",
    "repository",
    "schema",
    "settings",
    "stream",
    "tp",
    "types",
    "typing",
    "uow",
    "utils",
]

try:
    from . import logging  # noqa: F401

    __all__.append("logging")
except ImportError:
    pass

try:
    from . import testing  # noqa: F401

    __all__.append("testing")
except ImportError:
    pass

try:
    # TODO: `fastapi` 패키지에서 `import fastapi`를 사용하고 있어 발생하는 RUF100 규칙 위배 오류 해결
    # TODO: `import xxx` 대신 `importlib.util.find_spec()`을 사용하여 패키지 존재 여부 확인
    from . import fastapi  # noqa: F401, RUF100

    __all__.append("fastapi")
except ImportError:
    pass

try:
    from . import opentelemetry  # noqa: F401

    __all__.append("opentelemetry")
except ImportError:
    pass

try:
    from . import httpx  # noqa: F401

    __all__.append("httpx")
except ImportError:
    pass

try:
    import fastapi  # noqa: F401
except ImportError:
    raise ImportError("Install `fastapi` to use fastapi helpers")

from .endpoint import health_check
from .exception_handler import (
    ExceptionHandler,
    ExceptionHandlerInfo,
    create_exception_handler,
)
from .openapi import additional_responses, openapi_tags
from .param import as_query, to_query
from .response import NoContentResponse, ZipStreamingResponse
from .routing import APIRouter
from .security import APIKeyAuth, HTTPBasicAuth
from .wiring import auto_wired

__all__ = [
    "ExceptionHandler",
    "ExceptionHandlerInfo",
    "create_exception_handler",
    "to_query",
    "as_query",
    "health_check",
    "HTTPBasicAuth",
    "APIKeyAuth",
    "openapi_tags",
    "NoContentResponse",
    "ZipStreamingResponse",
    "APIRouter",
    "auto_wired",
    "additional_responses",
]


try:
    from .utils import (  # noqa: F401
        ErrorEvent,
        Level,
        capture_error,
        create_before_send_hook,
        init_sentry,
    )

    __all__.extend(
        [
            "ErrorEvent",
            "Level",
            "capture_error",
            "create_before_send_hook",
            "init_sentry",
        ]
    )
except ImportError:
    pass

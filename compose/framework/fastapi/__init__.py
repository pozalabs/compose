try:
    import fastapi  # noqa: F401
except ImportError:
    raise ImportError("Install `fastapi` to use fastapi helpers")

from .endpoint import health_check
from .exception_handler import (
    ExceptionHandler,
    ExceptionHandlerInfo,
    create_exception_handler,
    validation_error_handler,
)
from .openapi import openapi_tags
from .param import to_query
from .security import APIKeyAuth, HTTPBasicAuth

__all__ = [
    "ExceptionHandler",
    "ExceptionHandlerInfo",
    "create_exception_handler",
    "validation_error_handler",
    "to_query",
    "health_check",
    "HTTPBasicAuth",
    "APIKeyAuth",
    "openapi_tags",
]

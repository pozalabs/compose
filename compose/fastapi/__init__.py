try:
    from .endpoint import SpecialEndpoint, add_health_check_endpoint, health_check
    from .exception_handler import (
        ExceptionHandler,
        ExceptionHandlerInfo,
        create_exception_handler,
        default_exception_handlers,
    )
    from .openapi import (
        OpenAPIDoc,
        OpenAPISchema,
        RedocHTML,
        SwaggerUIHTML,
        add_doc_routes,
        additional_responses,
        openapi_tags,
    )
    from .otel import NonInstrumentedUrls
    from .param import FromAuth, FromPath, OffsetPaginationParams, as_query, with_fields
    from .response import NoContentResponse, ZipStreamingResponse
    from .routing import APIRouter
    from .security import APIKeyHeader, CookieAuth, HTTPBasic, HTTPBearer, unauthorized_error
except ImportError:
    raise ImportError("Install `fastapi` to use `compose.fastapi` package") from None

__all__ = [
    "APIKeyHeader",
    "APIRouter",
    "CookieAuth",
    "ExceptionHandler",
    "ExceptionHandlerInfo",
    "FromAuth",
    "FromPath",
    "HTTPBasic",
    "HTTPBearer",
    "NoContentResponse",
    "NonInstrumentedUrls",
    "OffsetPaginationParams",
    "OpenAPIDoc",
    "OpenAPISchema",
    "RedocHTML",
    "SpecialEndpoint",
    "SwaggerUIHTML",
    "ZipStreamingResponse",
    "add_doc_routes",
    "add_health_check_endpoint",
    "additional_responses",
    "as_query",
    "create_exception_handler",
    "default_exception_handlers",
    "health_check",
    "openapi_tags",
    "unauthorized_error",
    "with_fields",
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

try:
    from .routing import create_auto_wired_route  # noqa: F401
    from .wiring import auto_wired  # noqa: F401

    __all__.extend(["auto_wired", "create_auto_wired_route"])
except ImportError:
    pass

try:
    from .dishka import injected_route  # noqa: F401

    __all__.append("injected_route")
except ImportError:
    pass

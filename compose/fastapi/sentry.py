from __future__ import annotations

import enum
import functools
import inspect
from collections.abc import Awaitable, Callable, Sequence
from typing import TYPE_CHECKING, Self, cast

from fastapi import Request, Response

from compose import model

from .exception_handler import ExceptionHandler

try:
    import sentry_sdk
    from sentry_sdk.integrations import Integration
except ImportError:
    raise ImportError("Install 'sentry' extra to use sentry features") from None

if TYPE_CHECKING:
    from sentry_sdk.types import Event, Hint


class Level(enum.StrEnum):
    INFO = enum.auto()
    WARNING = enum.auto()
    ERROR = enum.auto()


class ErrorEvent(model.BaseModel):
    level: Level

    @classmethod
    def info(cls) -> Self:
        return cls(level=Level.INFO)

    @classmethod
    def warning(cls) -> Self:
        return cls(level=Level.WARNING)

    @classmethod
    def error(cls) -> Self:
        return cls(level=Level.ERROR)


type BeforeSendHook = Callable[[Event, Hint], Event | None]


def create_before_send_hook(
    errors: dict[str, ErrorEvent], default_error_level: Level = Level.WARNING
) -> BeforeSendHook:
    def before_send(event: Event, hint: Hint) -> Event | None:
        exc_name = ""
        if "exc_info" in hint:
            exc_type, *_ = hint["exc_info"]
            exc_name = exc_type.__name__

        error_event = errors.get(exc_name)
        event["level"] = default_error_level if error_event is None else error_event.level  # type: ignore[bad-assignment]
        return event

    return before_send


def init_sentry(
    dsn: str,
    integrations: Sequence[Integration],
    environment: str,
    tags: dict[str, str],
    before_send: BeforeSendHook | None = None,
    **kwargs,
) -> None:
    sentry_sdk.init(
        dsn=dsn,
        integrations=integrations,
        environment=environment,
        before_send=before_send,
        **kwargs,
    )
    scope = sentry_sdk.Scope.get_current_scope()
    for key, value in tags.items():
        scope.set_tag(key, value)


def capture_error(handler: ExceptionHandler) -> ExceptionHandler:
    if inspect.iscoroutinefunction(handler):

        @functools.wraps(handler)
        async def async_wrapper(request: Request, exc: Exception) -> Response:
            sentry_sdk.capture_exception(exc)
            return await cast(Awaitable[Response], handler(request, exc))

        return async_wrapper

    @functools.wraps(handler)
    async def wrapper(request: Request, exc: Exception) -> Response:
        sentry_sdk.capture_exception(exc)
        return cast(Response, handler(request, exc))

    return wrapper

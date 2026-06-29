import enum
import functools
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Self

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
    def for_info(cls) -> Self:
        return cls(level=Level.INFO)

    @classmethod
    def for_warning(cls) -> Self:
        return cls(level=Level.WARNING)

    @classmethod
    def for_error(cls) -> Self:
        return cls(level=Level.ERROR)


type BeforeSendHook = Callable[["Event", "Hint"], "Event | None"]


def create_before_send_hook(
    error: dict[str, ErrorEvent], default_error_level: Level = Level.WARNING
) -> BeforeSendHook:
    def before_send(event: "Event", hint: "Hint") -> "Event | None":
        exc_name = ""
        if "exc_info" in hint:
            exc_type, *_ = hint["exc_info"]
            exc_name = exc_type.__name__

        error_event = error.get(exc_name)
        event["level"] = default_error_level if error_event is None else error_event.level  # type: ignore[bad-assignment]
        return event

    return before_send


def init_sentry(
    dsn: str,
    integrations: list[Integration],
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
    @functools.wraps(handler)
    async def wrapper(request: Request, exc: Exception) -> Response:
        sentry_sdk.capture_exception(exc)
        result = handler(request, exc)
        if isinstance(result, Awaitable):
            return await result
        return result

    return wrapper

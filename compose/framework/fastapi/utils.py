import functools
from collections.abc import Awaitable

import sentry_sdk
from fastapi import Request, Response

from compose import fastapi


def capture_error(handler: fastapi.ExceptionHandler) -> fastapi.ExceptionHandler:
    @functools.wraps(handler)
    async def wrapper(request: Request, exc: Exception) -> Response | Awaitable[Response]:
        sentry_sdk.capture_exception(exc)
        result = handler(request, exc)
        if isinstance(result, Awaitable):
            return await result
        return result

    return wrapper

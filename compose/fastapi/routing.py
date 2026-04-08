import functools
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter as _FastAPIRouter

_OVERRIDE_DEFAULTS = {"response_model_by_alias": False}
_OVERRIDE_METHODS = {
    "get",
    "post",
    "put",
    "delete",
    "options",
    "head",
    "patch",
    "trace",
    "api_route",
    "add_api_route",
}


def _with_default_overrides[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        for key, value in _OVERRIDE_DEFAULTS.items():
            kwargs.setdefault(key, value)
        return func(*args, **kwargs)

    return wrapper


class APIRouter(_FastAPIRouter):
    pass


for _method_name in _OVERRIDE_METHODS:
    setattr(
        APIRouter,
        _method_name,
        _with_default_overrides(getattr(_FastAPIRouter, _method_name)),
    )


@functools.lru_cache(1)
def create_auto_wired_route(provider: Any) -> type:
    from fastapi.routing import APIRoute

    from .wiring import auto_wired

    class AutoWiredAPIRoute(APIRoute):
        def __init__(self, path: str, endpoint: Callable[..., Any], **kwargs: Any):
            super().__init__(
                path=path,
                endpoint=auto_wired(provider)(endpoint),
                **kwargs,
            )

    return AutoWiredAPIRoute

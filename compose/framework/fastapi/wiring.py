import inspect
from collections.abc import Callable
from typing import Any, TypeVar

from fastapi import Depends

from compose.dependency.wiring import Provider

F = TypeVar("F", bound=Callable[..., Any])


def auto_wired(provider: Provider) -> Callable[[F], F]:
    def wrapper(f: F) -> F:
        signature = inspect.signature(f)

        updated_params = []
        for name, param in signature.parameters.items():
            updated_param = param
            try:
                provided = provider(param.annotation)
                updated_param = updated_param.replace(default=Depends(provided))
            except ValueError:
                pass

            updated_params.append(updated_param)

        f.__signature__ = signature.replace(parameters=updated_params)

        return f

    return wrapper

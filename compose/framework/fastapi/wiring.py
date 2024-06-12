import inspect
from collections.abc import Callable
from typing import Any, TypeVar

from fastapi import Depends

from compose.dependency.wiring import Provider

F = TypeVar("F", bound=Callable[..., Any])


def auto_wired(provider: Provider) -> Callable[[F], F]:
    """
    FastAPI 엔드포인트에 의존성을 자동으로 주입하는 데코레이터. 해당 데코레이터는 `@inject` 데코레이터보다
    먼저 적용되어야 합니다.

    주의: `__signature__` 속성은 일반 함수에만 존재하므로 해당 데코레이터는 메서드에 사용할 수 없습니다.
    """

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

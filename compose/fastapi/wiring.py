import inspect
from collections.abc import Callable
from typing import Annotated, Any, Protocol

from dependency_injector.wiring import inject
from fastapi import Depends

from compose.di.dependency_injector.wiring import Provider


class HasSignature(Protocol):
    __signature__: inspect.Signature

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


def auto_wired[F: HasSignature](provider: Provider) -> Callable[[F], F]:
    """
    FastAPI 엔드포인트에 의존성을 자동으로 주입하는 데코레이터.

    주의: `__signature__` 속성은 일반 함수에만 존재하므로 해당 데코레이터는 메서드에 사용할 수 없습니다.
    """

    def wrapper(f: F) -> F:
        signature = inspect.signature(f)

        updated_params = []
        for name, param in signature.parameters.items():
            updated_param = param
            try:
                provided = provider(param.annotation)
                updated_param = updated_param.replace(
                    annotation=Annotated[param.annotation, Depends(provided)]
                )
            except ValueError:
                pass

            updated_params.append(updated_param)

        f.__signature__ = signature.replace(parameters=updated_params)
        f = inject(f)

        return f

    return wrapper

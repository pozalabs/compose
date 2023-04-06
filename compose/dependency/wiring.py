import functools
import inspect
from collections.abc import Iterable
from typing import Any, Optional, Protocol, TypeVar

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide

from compose.utils import deprecated

T = TypeVar("T")


class Wirer(Protocol):
    def __call__(
        self,
        container: containers.Container,
        modules: Optional[Iterable[str]] = None,
        from_package: Optional[str] = None,
    ) -> None:
        ...


def create_wirer(packages: Iterable[str]) -> Wirer:
    def wire_container(
        container: containers.Container,
        modules: Optional[Iterable[str]] = None,
        from_package: Optional[str] = None,
    ) -> None:
        container.check_dependencies()
        container.wire(modules=modules, packages=packages, from_package=from_package)

    return wire_container


@functools.lru_cache(32)
def resolve(type_: type[Any], container_cls: type[containers.Container]) -> providers.Factory:
    """
    의존성 전체 등록 경로를 참조하지 않고 의존성을 해결합니다. 다른 패키지의 의존성을 참조하는 경우
    의존 대상 선언 경로에 깊게 의존하는 것을 방지합니다. `container_cls`는 최상위 컨테이너일수도,
    의존성이 등록된 (하위) 컨테이너일수도 있습니다. 클래스 대상으로만 작동합니다.
    """
    if not inspect.isclass(type_):
        raise ValueError("Only class can be resolved")

    for provider in container_cls.traverse([providers.Factory]):
        provider_cls = provider.cls
        if not (inspect.isclass(provider_cls) or inspect.ismethod(provider_cls)):
            continue

        cls = provider_cls.__self__ if inspect.ismethod(provider_cls) else provider_cls
        if cls.__name__ == type_.__name__:  # type: ignore
            return provider

    raise ValueError(f"Cannot find {type_.__name__} from given container")


resolve_dependency = deprecated(
    "`resolve_dependency` is deprecated and will be removed in a future version. "
    "Use `resolve` instead."
)(resolve)


def provide(type_: type[T], from_: type[containers.Container], /) -> Provide[T]:
    return Provide[resolve(type_=type_, container_cls=from_)]  # type: ignore

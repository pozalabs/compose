import enum
import functools
import inspect
from collections.abc import Callable, Iterable
from typing import Any, Protocol, TypeVar

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide

T = TypeVar("T")


class Wirer(Protocol):
    def __call__(
        self,
        container: containers.Container,
        modules: Iterable[str] | None = None,
        from_package: str | None = None,
    ) -> None:
        ...


def create_wirer(packages: Iterable[str]) -> Wirer:
    def wire_container(
        container: containers.Container,
        modules: Iterable[str] | None = None,
        from_package: str | None = None,
    ) -> None:
        container.check_dependencies()
        container.wire(modules=modules, packages=packages, from_package=from_package)

    return wire_container


def resolve_by_name_from_container_provider(
    name: str, container: providers.Container
) -> providers.Factory:
    if not isinstance(name, str):
        raise ValueError("`name` must be string")

    for provider_name, provider in container.providers.items():
        if not isinstance(provider, (providers.Container, providers.Factory)):
            continue

        if provider_name == name:
            return provider

        if isinstance(provider, providers.Container):
            return resolve_by_name_from_container_provider(name=name, container=provider)


def resolve_by_name(
    name: str,
    container_cls: type[containers.Container],
) -> providers.Factory:
    if not isinstance(name, str):
        raise ValueError("`name` must be string")

    for provider_name, provider in container_cls.providers.items():
        if not isinstance(provider, (providers.Container, providers.Factory)):
            continue

        if provider_name == name:
            return provider

        if isinstance(provider, providers.Container):
            result = resolve_by_name_from_container_provider(name=name, container=provider)
            if result is not None:
                return result

    raise ValueError(f"Cannot find {name} from given container")


class ConflictResolution(str, enum.Enum):
    FIRST = "first"
    ERROR = "error"


@functools.lru_cache(32)
def resolve(
    type_: type[Any] | str,
    container_cls: type[containers.Container],
    *,
    name: str | None = None,
    conflict_resolution: ConflictResolution = ConflictResolution.FIRST,
) -> providers.Factory:
    """
    의존성 전체 등록 경로를 참조하지 않고 의존성을 해결합니다. 다른 패키지의 의존성을 참조하는 경우
    의존 대상 선언 경로에 깊게 의존하는 것을 방지합니다. `container_cls`는 최상위 컨테이너일수도,
    의존성이 등록된 (하위) 컨테이너일수도 있습니다. 클래스 대상으로만 작동합니다.
    """
    if not (inspect.isclass(type_) or isinstance(type_, str)):
        raise ValueError("Only class or string can be resolved")

    if isinstance(type_, str):
        return resolve_by_name(name=type_, container_cls=container_cls)

    candidates = []
    for provider in container_cls.traverse([providers.Factory]):
        provider_cls = provider.cls
        if not (inspect.isclass(provider_cls) or inspect.ismethod(provider_cls)):
            continue

        cls = provider_cls.__self__ if inspect.ismethod(provider_cls) else provider_cls
        if cls.__name__ == type_.__name__:
            candidates.append(provider)

    if not candidates:
        raise ValueError(f"Cannot find {type_.__name__} from given container")

    if len(candidates) > 1 and name is None and conflict_resolution == ConflictResolution.ERROR:
        type_name = type_.__name__ if inspect.isclass(type_) else type_
        raise ValueError(
            f"Cannot resolve {type_name} since there are multiple candidates. "
            f"You must specify `name` argument to resolve dependency"
        )

    if len(candidates) == 1:
        return candidates[0]

    if name is None and conflict_resolution == ConflictResolution.FIRST:
        return candidates[0]

    return resolve_by_name(name=name, container_cls=container_cls)


def provide(
    type_: type[T],
    from_: type[containers.Container],
    /,
    *,
    name: str | None = None,
    conflict_resolution: ConflictResolution = ConflictResolution.FIRST,
) -> Provide[T]:
    return Provide[
        resolve(
            type_=type_,
            container_cls=from_,
            name=name,
            conflict_resolution=conflict_resolution,
        )
    ]


def create_resolver(container_cls: type[containers.Container]) -> Callable[[str], Any]:
    def resolver(name: str) -> Any:
        return resolve(type_=name, container_cls=container_cls)

    return resolver

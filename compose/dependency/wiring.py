import importlib
import inspect
from collections.abc import Callable, Iterable
from typing import Any, Protocol

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide

type Container = type[containers.Container] | containers.Container

DEFAULT_RESOLVABLE_PROVIDER_TYPES = (providers.Factory, providers.Singleton)


def resolve_by_name_from_container_provider(
    name: str,
    container: providers.Container,
    provider_types: Iterable[type[providers.Provider]],
) -> providers.Provider | None:
    if not isinstance(name, str):
        raise ValueError("`name` must be string")

    for provider_name, provider in container.providers.items():  # type: ignore[union-attr]
        if not isinstance(provider, (providers.Container, *provider_types)):
            continue

        if provider_name == name:
            return provider

        if isinstance(provider, providers.Container):
            result = resolve_by_name_from_container_provider(
                name=name,
                container=provider,
                provider_types=provider_types,
            )
            if result is not None:
                return result

    return None


def resolve_by_name(
    name: str,
    container: Container,
    provider_types: Iterable[type[providers.Provider]],
) -> providers.Provider:
    if not isinstance(name, str):
        raise ValueError("`name` must be string")

    for provider_name, provider in container.providers.items():
        if not isinstance(provider, (providers.Container, *provider_types)):
            continue

        if provider_name == name:
            return provider

        if isinstance(provider, providers.Container):
            result = resolve_by_name_from_container_provider(
                name=name,
                container=provider,
                provider_types=provider_types,
            )
            if result is not None:
                return result

    raise ValueError(f"Cannot find {name} from given container")


def resolve_by_object_name(
    name: str,
    container: Container,
    provider_types: Iterable[type[providers.Provider]],
) -> Any:
    candidates: list[providers.Factory] = []
    for provider in container.traverse([*provider_types]):  # type: ignore[no-matching-overload]
        if not inspect.isclass(provider.cls):  # type: ignore[missing-attribute]
            continue

        if provider.cls.__name__.split(".")[-1] == name:  # type: ignore[missing-attribute]
            candidates.append(provider)  # type: ignore[bad-argument-type]

    if not candidates:
        raise ValueError(f"Cannot find {name} from given container")

    if len(candidates) > 1:
        raise ValueError(f"Cannot resolve {name} since there are multiple candidates")

    return candidates[0]()


def _collect_providers_by_type(
    type_: type,
    container: Container | providers.Container,
    provider_types: tuple[type[providers.Provider], ...],
) -> list[tuple[str, providers.Provider]]:
    candidates: list[tuple[str, providers.Provider]] = []
    for provider_name, provider in container.providers.items():  # type: ignore[union-attr]
        if isinstance(provider, providers.Container):
            candidates.extend(_collect_providers_by_type(type_, provider, provider_types))
        elif isinstance(provider, provider_types):
            provider_cls = provider.cls  # type: ignore[union-attr]
            if not (inspect.isclass(provider_cls) or inspect.ismethod(provider_cls)):
                continue
            cls = provider_cls.__self__ if inspect.ismethod(provider_cls) else provider_cls
            if cls.__name__ == type_.__name__:  # type: ignore[union-attr]
                candidates.append((provider_name, provider))
    return candidates


def resolve[T](
    type_: type[T],
    container: Container,
    provider_types: Iterable[type[providers.Provider]] = DEFAULT_RESOLVABLE_PROVIDER_TYPES,
    *,
    name: str | None = None,
) -> providers.Provider[T]:
    """
    의존성 전체 등록 경로를 참조하지 않고 의존성을 해결합니다. 다른 패키지의 의존성을 참조하는 경우
    의존 대상 선언 경로에 깊게 의존하는 것을 방지합니다. `container_cls`는 최상위 컨테이너일수도,
    의존성이 등록된 (하위) 컨테이너일수도 있습니다. 클래스 대상으로만 작동합니다.
    """
    if not inspect.isclass(type_):
        raise ValueError("Only class can be resolved")

    candidates = _collect_providers_by_type(type_, container, tuple(provider_types))

    if not candidates:
        raise ValueError(f"Cannot find {type_.__name__} from given container")

    if len(candidates) == 1:
        return candidates[0][1]  # type: ignore[return-value]

    if name is None:
        candidate_names = [n for n, _ in candidates]
        raise ValueError(
            f"Multiple providers found for {type_.__name__}: {candidate_names}. "
            f"Specify `name` to select one"
        )

    for candidate_name, provider in candidates:
        if candidate_name == name:
            return provider  # type: ignore[return-value]

    raise ValueError(
        f"Cannot find provider named '{name}' for {type_.__name__} from given container"
    )


def provide[T](
    type_: type[T],
    from_: type[containers.Container],
    /,
    *,
    provider_types: Iterable[type[providers.Provider]] = DEFAULT_RESOLVABLE_PROVIDER_TYPES,
    name: str | None = None,
) -> Provide[T]:
    return Provide[
        resolve(
            type_=type_,
            container=from_,
            provider_types=provider_types,
            name=name,
        )
    ]


def create_resolver(container: Container) -> Callable[[str], Any]:
    def resolver(name: str) -> Any:
        return resolve_by_name(
            name=name, container=container, provider_types=DEFAULT_RESOLVABLE_PROVIDER_TYPES
        )

    return resolver


def create_lazy_resolver(container_path: str) -> Callable[[str], Any]:
    def resolver(object_name: str) -> Any:
        module_path, container_name = container_path.split(":")
        try:
            container = importlib.import_module(module_path)
        except ImportError:
            raise ImportError(f"Cannot not import module {module_path}")

        if (container_cls := getattr(container, container_name, None)) is None:
            raise ValueError(f"Cannot find container {container_name} in {module_path}")

        return resolve_by_object_name(
            name=object_name,
            container=container_cls,
            provider_types=DEFAULT_RESOLVABLE_PROVIDER_TYPES,
        )

    return resolver


class Provider[T](Protocol):
    def __call__(
        self,
        t: type[T],
        /,
        name: str | None = None,
    ) -> Provide[T]: ...


def create_provider[T](
    container: type[containers.Container],
    provider_types: Iterable[type[providers.Provider]] = DEFAULT_RESOLVABLE_PROVIDER_TYPES,
) -> Provider[T]:
    def provider(
        type_: type[T],
        /,
        name: str | None = None,
    ) -> Provide[T]:
        return provide(
            type_,
            container,
            provider_types=provider_types,
            name=name,
        )

    return provider


def get_wiring_packages(*container_types: *tuple[type[containers.Container], ...]) -> set[str]:
    return {get_container_package(c) for c in container_types}


def get_container_package(container_type: type[containers.Container]) -> str:
    parts = container_type.__module__.split(".")

    if len(parts) >= 2:
        root, package, *_ = parts
        return f"{root}.{package}"

    raise ValueError(
        f"Invalid module path for {container_type.__name__}: expected 'root.package.*', got '{container_type.__module__}'"
    )

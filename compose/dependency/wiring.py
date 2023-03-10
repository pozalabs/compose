import inspect
from collections.abc import Callable
from typing import Any, Iterable, Optional

from dependency_injector import containers, providers


def create_wirer(packages: Iterable[str]) -> Callable[..., None]:
    def wire_container(
        container: containers.DeclarativeContainer,
        modules: Optional[Iterable[str]] = None,
        from_package: Optional[str] = None,
    ) -> None:
        container.check_dependencies()
        container.wire(modules=modules, packages=packages, from_package=from_package)

    return wire_container


def resolve_dependency(
    type_: type[Any], container_cls: type[containers.Container]
) -> providers.Factory:
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

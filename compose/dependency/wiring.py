import inspect
from collections.abc import Callable
from typing import Iterable, Optional, TypeVar

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide

T = TypeVar("T")


def create_wirer(packages: Iterable[str]) -> Callable[..., None]:
    def wire_container(
        container: containers.DeclarativeContainer,
        modules: Optional[Iterable[str]] = None,
        from_package: Optional[str] = None,
    ) -> None:
        container.check_dependencies()
        container.wire(modules=modules, packages=packages, from_package=from_package)

    return wire_container


def provide(container_cls: type[containers.Container], t: type[T]) -> Provide[providers.Factory]:
    if not inspect.isclass(t):
        raise ValueError("`t` must be class")

    for provider in container_cls.traverse([providers.Factory]):
        provider_cls = provider.cls
        if not (inspect.isclass(provider_cls) or inspect.ismethod(provider_cls)):
            continue

        cls = provider_cls.__self__ if inspect.ismethod(provider_cls) else provider_cls
        if cls.__name__ == t.__name__:  # type: ignore
            return Provide[provider]

    raise ValueError(f"Cannot find {t.__name__} from given container")

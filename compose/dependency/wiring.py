from collections.abc import Callable
from typing import Iterable, Optional

from dependency_injector import containers


def create_wirer(packages: Iterable[str]) -> Callable[..., None]:
    def wire_container(
        container: containers.DeclarativeContainer,
        modules: Optional[Iterable[str]] = None,
        from_package: Optional[str] = None,
    ) -> None:
        container.check_dependencies()
        container.wire(modules=modules, packages=packages, from_package=from_package)

    return wire_container

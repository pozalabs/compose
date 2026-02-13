from collections.abc import Iterable
from typing import Self

from dependency_injector import containers


class DeclarativeContainer(containers.DeclarativeContainer):
    @classmethod
    def wired(
        cls,
        packages: Iterable[str] = (),
        modules: Iterable[str] | None = None,
        from_package: str | None = None,
    ) -> Self:
        container = cls()
        container.check_dependencies()
        container.wire(modules=modules, packages=packages, from_package=from_package)
        return container

from collections.abc import Iterable
from typing import Self

from dependency_injector import containers


class DeclarativeContainer(containers.DeclarativeContainer):
    @classmethod
    def wired(
        cls,
        modules: Iterable[str] | None = None,
        packages: Iterable[str] = (),
        from_package: str | None = None,
        warn_unresolved: bool = False,
    ) -> Self:
        container = cls()
        container.check_dependencies()
        container.wire(
            modules=modules,
            packages=packages,
            from_package=from_package,
            warn_unresolved=warn_unresolved,
        )
        return container

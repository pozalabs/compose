from typing import Any

import pytest
from dependency_injector import containers, providers

from compose.dependency import provide


class RepositoryA:
    def __init__(self, name: str):
        self.name = name


class ApplicationContainer(containers.DeclarativeContainer):
    repository_a1 = providers.Factory(RepositoryA, name="repository_a1")
    repository_a2 = providers.Factory(RepositoryA, name="repository_a2")


@pytest.mark.parametrize(
    "type_, container_cls, name, expected",
    [
        (RepositoryA, ApplicationContainer, "repository_a1", RepositoryA(name="repository_a1")),
        (RepositoryA, ApplicationContainer, "repository_a2", RepositoryA(name="repository_a2")),
    ],
)
def test_provide_from_multiple_candidates(
    type_: type[Any],
    container_cls: type[containers.Container],
    name: str,
    expected: type[Any],
):
    provided = provide(type_, container_cls, name=name)

    assert provided.provider().__dict__ == expected.__dict__

from typing import TypeVar

import pytest
from dependency_injector import containers, providers

from compose.dependency import ConflictResolution, provide

T = TypeVar("T")


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
    type_: type[T],
    container_cls: type[containers.Container],
    name: str,
    expected: type[T],
):
    provided = provide(
        type_,
        container_cls,
        name=name,
        conflict_resolution=ConflictResolution.ERROR,
    )

    assert provided.provider().__dict__ == expected.__dict__

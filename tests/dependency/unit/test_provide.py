from collections.abc import Iterable
from typing import TypeVar

import pytest
from dependency_injector import containers, providers

from compose.dependency import ConflictResolution, provide
from compose.dependency.wiring import create_provider

T = TypeVar("T")


class RepositoryA:
    def __init__(self, name: str):
        self.name = name


class RepositoryB:
    def __init__(self, name: str):
        self.name = name


class RepositoryC:
    def __init__(self, name: str):
        self.name = name


class ApplicationContainer(containers.DeclarativeContainer):
    repository_a1 = providers.Factory(RepositoryA, name="repository_a1")
    repository_a2 = providers.Factory(RepositoryA, name="repository_a2")
    repository_b1 = providers.Singleton(RepositoryB, name="repository_b1")
    repository_c1 = providers.Factory(RepositoryC, name="repository_c1")


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


@pytest.mark.parametrize(
    "type_, container_cls, provider_types, expected",
    [
        (
            RepositoryB,
            ApplicationContainer,
            (providers.Factory, providers.Singleton),
            RepositoryB(name="repository_b1"),
        ),
        (
            RepositoryC,
            ApplicationContainer,
            (providers.Factory,),
            RepositoryC(name="repository_c1"),
        ),
    ],
)
def test_provide_with_provider_types(
    type_: type[T],
    container_cls: type[containers.Container],
    provider_types: Iterable[type[providers.Provider]],
    expected: type[T],
):
    provided = provide(
        type_,
        container_cls,
        provider_types=provider_types,
    )

    assert provided.provider().__dict__ == expected.__dict__


@pytest.mark.parametrize(
    "type_, container_cls, name, expected",
    [
        (RepositoryA, ApplicationContainer, "repository_a1", RepositoryA(name="repository_a1")),
    ],
)
def test_create_provider(
    type_: type[T],
    container_cls: type[containers.Container],
    name: str,
    expected: type[T],
):
    provider = create_provider(container_cls)
    provided = provider(
        type_,
        name=name,
        conflict_resolution=ConflictResolution.ERROR,
    )

    assert provided.provider().__dict__ == expected.__dict__

from __future__ import annotations

from typing import Any

import pytest
from dependency_injector import containers, providers

from compose.dependency import ConflictResolution, resolve


class Repository:
    ...


class RepositoryWithFactoryMethod:
    @classmethod
    def create(cls) -> RepositoryWithFactoryMethod:
        return cls()


def adder(a: int, b: int) -> int:
    return a + b


def id_generator(length: int) -> str:
    return "ABCDEF"[:length]


class RepositoryA:
    def __init__(self, name: str):
        self.name = name


class RepositoryB:
    def __init__(self, name: str):
        self.name = name


class NestedRepository:
    ...


class NestedContainer(containers.DeclarativeContainer):
    repository = providers.Factory(NestedRepository)
    repository_with_factory_method = providers.Factory(RepositoryWithFactoryMethod.create)
    id_generator = providers.Factory(id_generator, length=3)


class ApplicationContainer(containers.DeclarativeContainer):
    repository = providers.Factory(Repository)
    repository_a1 = providers.Factory(RepositoryA, name="repository_a1")
    repository_a2 = providers.Factory(RepositoryA, name="repository_a2")
    repository_b1 = providers.Singleton(RepositoryB, name="repository_b1")

    nested = providers.Container(NestedContainer)
    adder = providers.Factory(adder, a=1, b=2)


@pytest.mark.parametrize(
    "type_, container_cls, expected",
    [
        (Repository, ApplicationContainer, Repository),
        (NestedRepository, ApplicationContainer, NestedRepository),
        (NestedRepository, ApplicationContainer.nested, NestedRepository),
        (RepositoryWithFactoryMethod, ApplicationContainer, RepositoryWithFactoryMethod),
        (Repository, ApplicationContainer, Repository),
        ("repository", ApplicationContainer, Repository),
        ("repository", ApplicationContainer.nested, NestedRepository),
        ("repository_with_factory_method", ApplicationContainer, RepositoryWithFactoryMethod),
    ],
    ids=(
        "최상위 컨테이너에서 최상위 의존성 해결",
        "최상위 컨테이너에서 중첩 의존성 해결",
        "중첩 컨테이너에서 해당 컨테이너에 선언된 의존성 해결",
        "팩토리 메서드로 등록한 의존성 해결",
        "Factory 외의 Provider 의존성 해결",
        "의존성 등록 이름으로 의존성 해결",
        "중첩 컨테이너에서 의존성 등록 이름으로 의존성 해결",
        "의존성 등록 이름으로 팩토리 메서드 의존성 해결",
    ),
)
def test_resolve(
    type_: type[Any],
    container_cls: type[containers.Container],
    expected: type[Any],
):
    resolved = resolve(type_=type_, container=container_cls)

    assert isinstance(resolved.cls(), expected)


@pytest.mark.parametrize(
    "type_, container_cls, name, expected",
    [
        (RepositoryA, ApplicationContainer, "repository_a1", RepositoryA("repository_a1")),
        (RepositoryA, ApplicationContainer, "repository_a2", RepositoryA("repository_a2")),
    ],
)
def test_resolve_from_multiple_candidates(
    type_: type[Any],
    container_cls: type[containers.Container],
    name: str,
    expected: type[Any],
):
    resolved = resolve(
        type_=type_,
        container=container_cls,
        name=name,
        conflict_resolution=ConflictResolution.ERROR,
    )

    assert resolved().__dict__ == expected.__dict__


@pytest.mark.parametrize(
    "name, container_cls, expected",
    [
        ("adder", ApplicationContainer, 3),
        ("id_generator", ApplicationContainer, "ABC"),
        ("id_generator", ApplicationContainer.nested, "ABC"),
    ],
    ids=(
        "최상위 컨테이너에서 최상위 의존성 해결",
        "최상위 컨테이너에서 중첩 의존성 해결",
        "중첩 컨테이너에서 해당 컨테이너에 선언된 의존성 해결",
    ),
)
def test_resolve_func_by_name(
    name: str,
    container_cls: type[containers.Container],
    expected: Any,
):
    resolved = resolve(name, container_cls)  # type: ignore

    assert resolved() == expected


@pytest.mark.parametrize(
    "type_, container_cls",
    [
        (type("UnregisteredRepository"), ApplicationContainer),
        (Repository, ApplicationContainer.nested),
    ],
    ids=(
        "등록되지 않은 의존성은 해결할 수 없다",
        "상위 컨테이너에 선언된 의존성은 해결할 수 없다",
    ),
)
def test_cannot_resolve(type_: type[Any], container_cls: type[containers.Container]):
    with pytest.raises(ValueError):
        resolve(type_=type_, container=container_cls)


def test_cannot_resolve_without_name_from_multiple_candidates():
    with pytest.raises(ValueError):
        resolve(RepositoryA, ApplicationContainer, conflict_resolution=ConflictResolution.ERROR)

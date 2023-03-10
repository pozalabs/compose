from __future__ import annotations

from typing import Any

import pytest
from dependency_injector import containers, providers

from compose.dependency import resolve_dependency


class Repository:
    ...


class RepositoryWithFactoryMethod:
    @classmethod
    def create(cls) -> RepositoryWithFactoryMethod:
        return cls()


class NestedRepository:
    ...


class NestedContainer(containers.DeclarativeContainer):
    repository = providers.Factory(NestedRepository)
    repository_with_factory_method = providers.Factory(RepositoryWithFactoryMethod.create)


class ApplicationContainer(containers.DeclarativeContainer):
    repository = providers.Factory(Repository)

    nested = providers.Container(NestedContainer)


@pytest.mark.parametrize(
    "type_, container_cls, expected",
    [
        (Repository, ApplicationContainer, Repository),
        (NestedRepository, ApplicationContainer, NestedRepository),
        (NestedRepository, ApplicationContainer.nested, NestedRepository),
        (RepositoryWithFactoryMethod, ApplicationContainer, RepositoryWithFactoryMethod),
    ],
    ids=(
        "최상위 컨테이너에서 최상위 의존성 해결",
        "최상위 컨테이너에서 중첩 의존성 해결",
        "중첩 컨테이너에서 해당 컨테이너에 선언된 의존성 해결",
        "팩토리 메서드로 등록한 의존성 해결",
    ),
)
def test_resolve_dependency(
    type_: type[Any],
    container_cls: type[containers.Container],
    expected: type[Any],
):
    resolved = resolve_dependency(type_=type_, container_cls=container_cls)

    assert isinstance(resolved, providers.Factory)
    assert resolved.cls == expected


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
def test_cannot_resolve_dependency(type_: type[Any], container_cls: type[containers.Container]):
    with pytest.raises(ValueError):
        resolve_dependency(type_=type, container_cls=container_cls)

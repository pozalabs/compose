import operator
from typing import Any

import pytest
from dependency_injector import containers, providers

from compose.dependency import resolve_by_object_name


class Repository:
    ...


class RepositoryA:
    def __init__(self, name: str):
        self.name = name


class ApplicationContainer(containers.DeclarativeContainer):
    repository = providers.Factory(Repository)
    repository_a1 = providers.Factory(RepositoryA, name="repository_a1")
    repository_a2 = providers.Factory(RepositoryA, name="repository_a2")

    adder = providers.Factory(operator.add, a=1, b=2)


@pytest.mark.parametrize(
    "object_name, expected",
    [
        ("Repository", Repository),
    ],
)
def test_resolve_by_object_name(object_name: str, expected: type[Any]):
    actual = resolve_by_object_name(
        name=object_name,
        container=ApplicationContainer,
        provider_types=(providers.Factory, providers.Singleton),
    )

    assert isinstance(actual, expected)


@pytest.mark.parametrize(
    "object_name, container_cls",
    [
        ("adder", ApplicationContainer),
        ("RepositoryA", ApplicationContainer),
    ],
    ids=(
        "함수는 의존성을 해결할 수 없다",
        "동일한 클래스가 여러 개 등록되어 있으면 의존성을 해결할 수 없다",
    ),
)
def test_cannot_resolve_by_object_name(object_name: str, container_cls: type[containers.Container]):
    with pytest.raises(ValueError):
        resolve_by_object_name(
            name=object_name,
            container=container_cls,
            provider_types=(providers.Factory, providers.Singleton),
        )

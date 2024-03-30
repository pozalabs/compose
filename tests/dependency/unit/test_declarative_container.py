import pytest
from dependency_injector import providers
from dependency_injector.wiring import inject

import compose


class Adder:
    def __init__(self, initial: int):
        self.initial = initial

    def add(self, v: int) -> int:
        return self.initial + v


class ApplicationContainer(compose.dependency.DeclarativeContainer):
    adder = providers.Factory(Adder, initial=1)


@pytest.fixture
def container():
    wirer = compose.dependency.create_wirer(packages=[])
    container = ApplicationContainer.wired(wirer=wirer, modules=[__name__])
    yield container
    container.unwire()


@inject
def add(
    v: int,
    adder: Adder = compose.dependency.provide(Adder, ApplicationContainer),
) -> int:
    return adder.add(v)


@pytest.mark.usefixtures("container")
def test_wired():
    assert add(2) == 3


def test_cannot_inject_without_wiring():
    with pytest.raises(AttributeError) as exc_info:
        add(2)

    assert "'Provide' object has no attribute" in str(exc_info.value)

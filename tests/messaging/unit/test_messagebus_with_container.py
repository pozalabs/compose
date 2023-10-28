import functools

import pytest
from dependency_injector import containers, providers

import compose
from compose.messaging.messagebus import MessageBus


class SomethingHappened(compose.event.Event):
    ...


class SomethingHappenedHandler:
    def handle(self, evt: SomethingHappened) -> None:
        ...


class ApplicationContainer(containers.DeclarativeContainer):
    something_happened_handler = providers.Factory(SomethingHappenedHandler)


@pytest.fixture
def with_container() -> MessageBus | None:
    try:
        return MessageBus.with_container(
            "tests.messaging.unit.test_messagebus_with_container:ApplicationContainer"
        )
    except (ValueError, ImportError):
        return None


def test_with_container():
    result = compose.result.to_result(
        functools.partial(
            MessageBus.with_container,
            "tests.messaging.unit.test_messagebus_with_container:ApplicationContainer",
        )
    )

    assert result.unwrap_or(None) is not None

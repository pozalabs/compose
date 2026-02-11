from dependency_injector import containers, providers

import compose
from compose.messaging.messagebus import MessageBus


class SomethingHappened(compose.event.MongoEvent): ...


class SomethingHappenedHandler:
    def handle(self, evt: SomethingHappened) -> None: ...


class ApplicationContainer(containers.DeclarativeContainer):
    something_happened_handler = providers.Factory(SomethingHappenedHandler)


def test_with_container():
    def init_messagebus() -> MessageBus | None:
        try:
            return MessageBus.with_container(
                "tests.messaging.unit.test_messagebus_with_container:ApplicationContainer"
            )
        except ValueError:
            return None

    assert init_messagebus() is not None

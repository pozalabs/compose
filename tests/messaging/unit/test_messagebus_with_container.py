from dependency_injector import containers, providers

import compose
from compose.messaging.event_bus import EventBus


class SomethingHappened(compose.event.Event[compose.types.PyObjectId]):
    id: compose.types.PyObjectId = compose.field.IdField(default_factory=compose.types.PyObjectId)


class SomethingHappenedHandler:
    async def handle(self, evt: SomethingHappened) -> None: ...


class ApplicationContainer(containers.DeclarativeContainer):
    something_happened_handler = providers.Factory(SomethingHappenedHandler)


def test_with_container():
    def init_messagebus() -> EventBus | None:
        try:
            return EventBus.with_container(
                "tests.messaging.unit.test_messagebus_with_container:ApplicationContainer"
            )
        except ValueError:
            return None

    assert init_messagebus() is not None

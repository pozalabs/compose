import pytest
from dependency_injector import containers, providers

import compose
from compose.di.dependency_injector.wiring import create_event_handler_resolver
from compose.messaging.event_bus import EventBus


class SomethingHappened(compose.event.Event[compose.types.PyObjectId]):
    id: compose.types.PyObjectId = compose.field.PyObjectIdField(
        default_factory=compose.types.PyObjectId
    )


class SomethingHappenedHandler:
    async def handle(self, evt: SomethingHappened) -> None: ...


class ApplicationContainer(containers.DeclarativeContainer):
    something_happened_handler = providers.Factory(SomethingHappenedHandler)


def test_create_event_bus_with_resolver():
    resolver = create_event_handler_resolver(ApplicationContainer)
    event_bus = EventBus(dependency_resolver=resolver)

    assert event_bus is not None


@pytest.mark.asyncio
async def test_resolve_and_handle_event():
    resolver = create_event_handler_resolver(ApplicationContainer)
    event_bus = EventBus(dependency_resolver=resolver)
    event_bus.register(SomethingHappened)(SomethingHappenedHandler)

    await event_bus.handle_event(SomethingHappened())


def test_cannot_register_duplicate_handler():
    async def resolver(handler_type):
        return handler_type()

    event_bus = EventBus(dependency_resolver=resolver)
    event_bus.register(SomethingHappened)(SomethingHappenedHandler)

    with pytest.raises(ValueError, match="already registered"):
        event_bus.register(SomethingHappened)(SomethingHappenedHandler)


@pytest.mark.asyncio
async def test_handle_unregistered_event():
    called = False

    async def resolver(handler_type):
        nonlocal called
        called = True
        return handler_type()

    event_bus = EventBus(dependency_resolver=resolver)

    await event_bus.handle_event(SomethingHappened())

    assert called is False

import pytest
from dependency_injector import containers, providers

from compose.di.dependency_injector.wiring import create_event_handler_resolver


class FakeHandler:
    async def handle(self, evt) -> None: ...


class AppContainer(containers.DeclarativeContainer):
    fake_handler = providers.Factory(FakeHandler)


@pytest.mark.asyncio
async def test_resolve_handler_by_type():
    resolver = create_event_handler_resolver(AppContainer)
    handler = await resolver(FakeHandler)

    assert isinstance(handler, FakeHandler)

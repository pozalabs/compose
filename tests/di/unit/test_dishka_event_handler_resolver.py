import pytest
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide

from compose.di.dishka import create_event_handler_resolver


class FakeHandler:
    async def handle(self, evt) -> None: ...


class HandlerProvider(Provider):
    scope = Scope.APP

    fake_handler = provide(FakeHandler)


@pytest.fixture
def container():
    return make_async_container(HandlerProvider())


@pytest.mark.asyncio
async def test_resolve_handler_by_type(container: AsyncContainer):
    resolver = create_event_handler_resolver(container)
    handler = await resolver(FakeHandler)
    await container.close()

    assert isinstance(handler, FakeHandler)

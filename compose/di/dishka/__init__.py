from collections.abc import Awaitable, Callable
from typing import Any

from dishka import AsyncContainer


def create_event_handler_resolver(container: AsyncContainer) -> Callable[[type], Awaitable[Any]]:
    async def resolver(handler_type: type) -> Any:
        return await container.get(handler_type)

    return resolver

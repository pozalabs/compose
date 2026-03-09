import collections
from collections.abc import Awaitable, Callable
from typing import Protocol

from compose.event import Event


class EventHandler(Protocol):
    async def handle(self, evt: Event) -> None: ...


class EventBus:
    def __init__(
        self, dependency_resolver: Callable[[type[EventHandler]], Awaitable[EventHandler]]
    ):
        self.dependency_resolver = dependency_resolver

        self._event_handlers: dict[str, set[type[EventHandler]]] = collections.defaultdict(set)

    async def handle_event(self, evt: Event) -> None:
        handler_types = self._event_handlers.get(evt.__class__.__name__, set())
        for handler_type in handler_types:
            handler = await self.dependency_resolver(handler_type)
            await handler.handle(evt)

    def register(
        self, event_cls: type[Event]
    ) -> Callable[[type[EventHandler]], type[EventHandler]]:
        def wrapper(handler_cls: type[EventHandler]) -> type[EventHandler]:
            event_name = event_cls.__name__

            registered_handler_types = self._event_handlers.get(event_name, set())
            if handler_cls in registered_handler_types:
                raise ValueError(
                    f"Handler `{handler_cls.__name__}` already registered for event `{event_name}`"
                )

            self._event_handlers[event_name].add(handler_cls)
            return handler_cls

        return wrapper

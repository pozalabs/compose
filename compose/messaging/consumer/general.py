import asyncio
import logging

from compose import types

from .. import model
from ..event_bus import EventBus
from ..queue.base import MessageQueue
from ..signal_handler import DefaultSignalHandler, SignalHandler
from .hook import DEFAULT_HOOKS, Hook, HookArgType, HookEventType, default_hook

logger = logging.getLogger("compose")


class MessageConsumer:
    def __init__(
        self,
        event_bus: EventBus,
        message_queue: MessageQueue,
        hooks: dict[HookEventType, list[Hook]] | None = None,
        signal_handler: SignalHandler | None = None,
        max_receive_backoff: types.Seconds = types.Seconds(60),
    ):
        self.event_bus = event_bus
        self.message_queue = message_queue
        self.hooks = DEFAULT_HOOKS | (hooks or {})
        self.signal_handler = signal_handler or DefaultSignalHandler()
        self._max_receive_backoff = max_receive_backoff

        self._default_hook = default_hook

    async def run(self) -> None:
        self._execute_hook("on_start", "MessageConsumer started")
        consecutive_failures = 0

        while not self.signal_handler.received_signal:
            try:
                message = self.message_queue.peek()
            except Exception as exc:
                consecutive_failures += 1
                self._execute_hook("on_receive_error", exc)
                await self._backoff_wait(min(2**consecutive_failures, self._max_receive_backoff))
                continue

            consecutive_failures = 0

            if message is None:
                continue
            self._execute_hook("on_receive", message)

            try:
                await asyncio.create_task(self.consume(message))
            except Exception as exc:
                self._execute_hook("on_consume_error", exc)
                continue
            self._execute_hook("on_consume", message)

    async def consume(self, message: model.EventMessage) -> None:
        await self.event_bus.handle_event(message.body)
        self.message_queue.delete(message)

    async def _backoff_wait(self, delay: float) -> None:
        remaining = delay
        while remaining > 0 and not self.signal_handler.received_signal:
            await asyncio.sleep(min(remaining, 0.5))
            remaining -= 0.5

    def _execute_hook(self, hook_event_type: HookEventType, arg: HookArgType, /) -> None:
        for hook in self.hooks.get(hook_event_type, [self._default_hook]):
            hook(arg)

    def shutdown(self) -> None:
        self._execute_hook("on_shutdown", "MessageConsumer shutting down")
        self.signal_handler.handle()

import asyncio
import json
import logging
from collections.abc import Callable
from typing import Literal, TypeAlias

from . import model
from .messagebus import MessageBus
from .queue import MessageQueue
from .signal_handler import DefaultSignalHandler, SignalHandler

HookEventType = Literal[
    "on_start",
    "on_receive",
    "on_receive_error",
    "on_consume",
    "on_consume_error",
    "on_shutdown",
]
HookArgType: TypeAlias = str | model.EventMessage | Exception
Hook: TypeAlias = Callable[[HookArgType], None]

logger = logging.getLogger("compose")


def log_event_message(log_message: str, message: model.EventMessage) -> None:
    logger.info(
        f"{log_message}: {json.dumps(message.encode(), ensure_ascii=False)}",
        extra={"event_message": message.encode()},
    )


def log_exception(log_message: str, exc: Exception) -> None:
    logger.exception(log_message, exc_info=exc, stack_info=True)


DEFAULT_HOOKS = {
    "on_start": [logger.info],
    "on_receive": [lambda message: log_event_message("Received message", message)],
    "on_receive_error": [lambda exc: log_exception("Failed to receive message", exc)],
    "on_consume": [lambda message: log_event_message("Consumed message", message)],
    "on_consume_error": [lambda exc: log_exception(f"Failed to consume message due to {exc}", exc)],
    "on_shutdown": [logger.info],
}


class MessageConsumer:
    def __init__(
        self,
        messagebus: MessageBus,
        message_queue: MessageQueue,
        hooks: dict[HookEventType, list[Hook]] | None = None,
        signal_handler: SignalHandler | None = None,
    ):
        self.messagebus = messagebus
        self.message_queue = message_queue
        self.hooks = DEFAULT_HOOKS | (hooks or {})
        self.signal_handler = signal_handler or DefaultSignalHandler()

        self._default_hook = lambda _: None

    async def run(self) -> None:
        self._execute_hook("on_start", "MessageConsumer started")

        while not self.signal_handler.received_signal:
            try:
                message = self.message_queue.peek()
            except Exception as exc:
                self._execute_hook("on_receive_error", exc)
                continue

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
        await self.messagebus.handle_event(message.body)
        self.message_queue.delete(message)

    def _execute_hook(self, hook_event_type: HookEventType, arg: HookArgType, /) -> None:
        for hook in self.hooks.get(hook_event_type, [self._default_hook]):
            hook(arg)

    def shutdown(self) -> None:
        self._execute_hook("on_shutdown", "MessageConsumer shutting down")
        self.signal_handler.handle()

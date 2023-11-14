import asyncio
import sys
import threading
from collections.abc import Callable
from typing import Literal

from . import model
from .messagebus import MessageBus
from .queue import MessageQueue

CAN_USE_ASYNCIO_RUNNER = sys.version_info >= (3, 11)

HookEventType = Literal["on_receive", "on_receive_error", "on_consume", "on_consume_error"]
Hook = Callable[[model.EventMessage | Exception], None]


class MessageConsumer:
    def __init__(
        self,
        messagebus: MessageBus,
        message_queue: MessageQueue,
        hooks: dict[HookEventType, list[Hook]] | None = None,
    ):
        self.messagebus = messagebus
        self.message_queue = message_queue
        self.hooks = hooks or {}

        self._default_hook = lambda _: None

    async def run(self) -> None:
        while True:
            try:
                message = self.message_queue.peek()
            except Exception as exc:
                self._execute_hook(hook_event_type="on_receive_error", message=exc)
                continue

            self._execute_hook(hook_event_type="on_receive", message=message)
            if message is None:
                continue

            try:
                await asyncio.create_task(self.consume(message))
            except Exception as exc:
                self._execute_hook(hook_event_type="on_consume_error", message=exc)
                continue
            self._execute_hook(hook_event_type="on_consume", message=message)

    async def consume(self, message: model.EventMessage) -> None:
        await self.messagebus.handle_event(message.body)
        self.message_queue.delete(message)

    def _execute_hook(
        self,
        hook_event_type: HookEventType,
        message: model.EventMessage | Exception,
    ) -> None:
        for hook in self.hooks.get(hook_event_type, [self._default_hook]):
            hook(message)


class MessageConsumerRunner:
    def __init__(self, message_consumer_factory: Callable[[], MessageConsumer]):
        self.message_consumer_factory = message_consumer_factory

    def run(self, num_threads: int = 1) -> None:
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=self._run_in_thread)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    def _run_in_thread(self) -> None:
        if CAN_USE_ASYNCIO_RUNNER:
            with asyncio.Runner() as runner:
                runner.run(self._run_consumer())
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._run_consumer())

    async def _run_consumer(self) -> None:
        message_consumer = self.message_consumer_factory()
        await message_consumer.run()

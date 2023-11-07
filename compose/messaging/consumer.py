import asyncio
import sys
import threading
from collections.abc import Callable

from . import model
from .messagebus import MessageBus
from .queue import MessageQueue

CAN_USE_ASYNCIO_RUNNER = sys.version_info >= (3, 11)


class MessageConsumer:
    def __init__(self, messagebus: MessageBus, message_queue: MessageQueue):
        self.messagebus = messagebus
        self.message_queue = message_queue

    async def run(self) -> None:
        while True:
            try:
                message = self.message_queue.peek()
            except Exception:
                continue

            if message is None:
                continue

            try:
                await asyncio.create_task(self.consume(message))
            except Exception:
                continue

    async def consume(self, message: model.EventMessage) -> None:
        await self.messagebus.handle_event(message.body)
        self.message_queue.delete(message)


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

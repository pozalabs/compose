import asyncio
import sys
import threading
from collections.abc import Callable

from .consumer import MessageConsumer

CAN_USE_ASYNCIO_RUNNER = sys.version_info >= (3, 11)


class MessageConsumerThreadRunner:
    def __init__(self, message_consumer_factory: Callable[[], MessageConsumer]):
        self.message_consumer_factory = message_consumer_factory

    def run(self, num_workers: int = 1) -> None:
        threads = []
        for _ in range(num_workers):
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

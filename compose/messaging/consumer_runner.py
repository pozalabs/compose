import asyncio
import logging
import signal
import sys
import threading
import time
import types
from collections.abc import Callable

from .consumer import MessageConsumer
from .signal_handler import SignalHandler, ThreadSignalHandler

CAN_USE_ASYNCIO_RUNNER = sys.version_info >= (3, 11)

logger = logging.getLogger("compose")


class MessageConsumerThreadRunner:
    def __init__(
        self,
        message_consumer_factory: Callable[[], MessageConsumer],
        signal_handler_factory: Callable[[], SignalHandler] = ThreadSignalHandler,
    ):
        self.message_consumer_factory = message_consumer_factory
        self.signal_handler_factory = signal_handler_factory

        self._received_signal = False

        for signum in (signal.SIGINT, signal.SIGTERM):
            signal.signal(signum, self.handle_signal)

    def run(self, num_workers: int = 1) -> None:
        threads = []
        signal_handlers = []

        for _ in range(num_workers):
            signal_handler = self.signal_handler_factory()
            t = threading.Thread(
                target=self._run_in_thread,
                kwargs={"signal_handler": signal_handler},
            )
            t.start()
            threads.append(t)
            signal_handlers.append(signal_handler)

        while not self._received_signal:
            time.sleep(0.5)

        for signal_handler in signal_handlers:
            signal_handler.handle()

        for t in threads:
            t.join()

    def _run_in_thread(self, signal_handler: SignalHandler) -> None:
        if CAN_USE_ASYNCIO_RUNNER:
            with asyncio.Runner() as runner:
                runner.run(self._run_consumer(signal_handler))
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._run_consumer(signal_handler))

    async def _run_consumer(self, signal_handler: SignalHandler) -> None:
        message_consumer = self.message_consumer_factory()
        await message_consumer.run(signal_handler)

    def handle_signal(self, signum: int, _: types.FrameType) -> None:
        logger.info(f"Received {signal.Signals(signum).name}, exiting gracefully")
        self._received_signal = True

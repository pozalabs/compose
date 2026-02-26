from unittest.mock import AsyncMock, patch

import pytest

from compose.messaging.consumer.general import MessageConsumer
from compose.messaging.consumer.hook import default_hook
from compose.messaging.model import EventMessage
from compose.messaging.queue.base import MessageQueue
from compose.messaging.signal_handler import DefaultSignalHandler


class FakeMessageQueue(MessageQueue):
    def __init__(self, results: list[EventMessage | Exception | None]):
        self._results = list(results)
        self._index = 0

    def push(self, message: EventMessage) -> None:
        raise NotImplementedError

    def peek(self) -> EventMessage | None:
        if self._index >= len(self._results):
            raise StopIteration
        result = self._results[self._index]
        self._index += 1
        if isinstance(result, Exception):
            raise result
        return result

    def delete(self, message: EventMessage) -> None: ...


class StopAfterSignalHandler(DefaultSignalHandler):
    """Signal handler that stops the loop after a set number of peek calls."""

    def __init__(self, stop_after: int):
        super().__init__()
        self._stop_after = stop_after
        self._call_count = 0

    def tick(self) -> None:
        self._call_count += 1
        if self._call_count >= self._stop_after:
            self.handle()


def _make_consumer(
    results: list[EventMessage | Exception | None],
    stop_after: int,
    max_receive_backoff: float = 60.0,
) -> MessageConsumer:
    signal_handler = StopAfterSignalHandler(stop_after)
    queue = FakeMessageQueue(results)

    original_peek = queue.peek

    def peek_with_tick() -> EventMessage | None:
        signal_handler.tick()
        return original_peek()

    queue.peek = peek_with_tick  # type: ignore[method-assign]

    hooks = {
        "on_start": [default_hook],
        "on_receive_error": [default_hook],
        "on_shutdown": [default_hook],
    }
    return MessageConsumer(
        messagebus=AsyncMock(),
        message_queue=queue,
        hooks=hooks,
        signal_handler=signal_handler,
        max_receive_backoff=max_receive_backoff,
    )


@pytest.mark.asyncio
@pytest.mark.unit
async def test_backoff_on_consecutive_peek_failures():
    consumer = _make_consumer(
        results=[RuntimeError(), RuntimeError(), RuntimeError()],
        stop_after=3,
    )

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await consumer.run()

    delays = [call.args[0] for call in mock_sleep.call_args_list]
    # 1st failure: 2^1=2, split into 0.5 chunks -> [0.5, 0.5, 0.5, 0.5]
    # 2nd failure: 2^2=4, split into 0.5 chunks -> [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    # 3rd failure: signal fires, backoff wait still called but signal check stops it
    total_wait = sum(delays)
    assert total_wait == pytest.approx(6.0, abs=0.5)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_backoff_reset_on_successful_peek():
    consumer = _make_consumer(
        results=[RuntimeError(), None, RuntimeError(), None],
        stop_after=4,
    )

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await consumer.run()

    delays = [call.args[0] for call in mock_sleep.call_args_list]
    # 1st failure: 2^1=2s
    # success: reset
    # 2nd failure: 2^1=2s (reset, not 2^2=4s)
    total_wait = sum(delays)
    assert total_wait == pytest.approx(4.0, abs=0.5)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_backoff_respect_signal_handler():
    signal_handler = DefaultSignalHandler()
    queue = FakeMessageQueue([RuntimeError()])

    consumer = MessageConsumer(
        messagebus=AsyncMock(),
        message_queue=queue,
        hooks={"on_start": [default_hook], "on_receive_error": [default_hook]},
        signal_handler=signal_handler,
        max_receive_backoff=60.0,
    )

    async def signal_after_first_sleep(_delay: float) -> None:
        signal_handler.handle()

    with patch("asyncio.sleep", side_effect=signal_after_first_sleep):
        await consumer.run()

    assert signal_handler.received_signal


@pytest.mark.asyncio
@pytest.mark.unit
async def test_backoff_capped_at_max():
    max_backoff = 10.0
    consumer = _make_consumer(
        results=[RuntimeError()] * 20,
        stop_after=20,
        max_receive_backoff=max_backoff,
    )

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await consumer.run()

    delays = [call.args[0] for call in mock_sleep.call_args_list]
    assert all(d <= max_backoff for d in delays)

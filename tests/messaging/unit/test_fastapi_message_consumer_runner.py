import asyncio
import contextlib
import threading
import time

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

import compose


class FakeMessageConsumer:
    def __init__(self):
        self.run_called = False
        self.shutdown_called = False
        self._shutdown_event = threading.Event()

    async def run(self):
        self.run_called = True
        while not self._shutdown_event.is_set():
            await asyncio.sleep(0.01)

    async def consume(self, message: compose.messaging.EventMessage) -> None: ...

    def shutdown(self):
        self.shutdown_called = True
        self._shutdown_event.set()


class SlowStartupFakeConsumer(FakeMessageConsumer):
    def __init__(self, startup_delay: float = 0.5):
        super().__init__()
        self.startup_delay = startup_delay

    async def run(self):
        await asyncio.sleep(self.startup_delay)
        await super().run()


class FailingFakeConsumer(FakeMessageConsumer):
    def __init__(self, error: Exception):
        super().__init__()
        self.error = error

    async def run(self):
        self.run_called = True
        raise self.error


@pytest.fixture
def fake_consumer() -> FakeMessageConsumer:
    return FakeMessageConsumer()


@pytest.fixture
def runner(fake_consumer: FakeMessageConsumer) -> compose.messaging.FastAPIMessageConsumerRunner:
    return compose.messaging.FastAPIMessageConsumerRunner(
        message_consumer_factory=lambda: fake_consumer,
    )


def test_lifespan_runs_consumer(
    runner: compose.messaging.FastAPIMessageConsumerRunner,
    fake_consumer: FakeMessageConsumer,
):
    with runner.lifespan():
        _wait_until(lambda: fake_consumer.run_called)
        assert fake_consumer.run_called


def test_lifespan_shuts_down_consumer(
    runner: compose.messaging.FastAPIMessageConsumerRunner,
    fake_consumer: FakeMessageConsumer,
):
    with runner.lifespan():
        _wait_until(lambda: fake_consumer.run_called)

    assert fake_consumer.shutdown_called


def test_lifespan_graceful_shutdown_before_consumer_ready():
    slow_consumer = SlowStartupFakeConsumer(startup_delay=0.2)
    runner = compose.messaging.FastAPIMessageConsumerRunner(
        message_consumer_factory=lambda: slow_consumer,
    )

    with runner.lifespan(timeout=1):
        pass


@pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
def test_lifespan_handles_consumer_exception():
    failing_consumer = FailingFakeConsumer(RuntimeError("Consumer crashed"))
    runner = compose.messaging.FastAPIMessageConsumerRunner(
        message_consumer_factory=lambda: failing_consumer,
    )

    with runner.lifespan():
        _wait_until(lambda: failing_consumer.run_called)

    assert failing_consumer.shutdown_called


@pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
def test_lifespan_handles_factory_exception():
    factory_called = False

    def failing_factory():
        nonlocal factory_called
        factory_called = True
        raise ValueError("Factory failed")

    runner = compose.messaging.FastAPIMessageConsumerRunner(
        message_consumer_factory=failing_factory,
    )

    with runner.lifespan():
        _wait_until(lambda: factory_called)


def test_lifespan_can_be_reused():
    consumers: list[FakeMessageConsumer] = []

    def consumer_factory():
        consumer = FakeMessageConsumer()
        consumers.append(consumer)
        return consumer

    runner = compose.messaging.FastAPIMessageConsumerRunner(
        message_consumer_factory=consumer_factory,
    )

    with runner.lifespan():
        _wait_until(lambda: len(consumers) > 0 and consumers[0].run_called)

    assert consumers[0].shutdown_called

    with runner.lifespan():
        _wait_until(lambda: len(consumers) > 1 and consumers[1].run_called)

    assert consumers[1].shutdown_called
    assert len(consumers) == 2


def test_lifespan_with_fastapi():
    fake_consumer = FakeMessageConsumer()
    runner = compose.messaging.FastAPIMessageConsumerRunner(
        message_consumer_factory=lambda: fake_consumer,
    )

    @contextlib.asynccontextmanager
    async def lifespan(_app: FastAPI):
        with runner.lifespan():
            yield

    app = FastAPI(lifespan=lifespan)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200

        _wait_until(lambda: fake_consumer.run_called)
        assert fake_consumer.run_called

    assert fake_consumer.shutdown_called


def _wait_until(condition, timeout: float = 5.0, interval: float = 0.01):
    start = time.time()
    while not condition() and (time.time() - start) < timeout:
        time.sleep(interval)

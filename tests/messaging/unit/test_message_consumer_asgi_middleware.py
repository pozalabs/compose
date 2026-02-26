import logging

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

import compose
from compose.messaging.event_bus import EventHandler


def event_handler_dependency_resolver(handler_name: str) -> EventHandler:
    return globals()[handler_name]()


event_bus = compose.messaging.EventBus(event_handler_dependency_resolver)
message_queue = compose.messaging.LocalMessageQueue()


class OrderPlaced(compose.event.Event[compose.types.PyObjectId]):
    id: compose.types.PyObjectId = compose.field.IdField(default_factory=compose.types.PyObjectId)
    sku: str


@event_bus.register(OrderPlaced)
class OrderPlacedHandler:
    async def handle(self, evt: OrderPlaced) -> None: ...


class PlaceOrder(compose.command.Command):
    sku: str


class PlaceOrderHandler:
    def __init__(self, event_publisher: compose.messaging.EventPublisher):
        self.event_publisher = event_publisher

    def handle(self, cmd: PlaceOrder) -> None:
        self.event_publisher.publish(OrderPlaced(sku=cmd.sku))


@pytest.fixture
def app() -> FastAPI:
    _app = FastAPI()
    _app.add_middleware(
        compose.messaging.MessageConsumerASGIMiddleware,
        event_bus=event_bus,
        message_queue=message_queue,
    )

    @_app.post("/orders")
    def place_order(cmd: PlaceOrder):
        handler = PlaceOrderHandler(event_publisher=compose.messaging.EventPublisher(message_queue))
        handler.handle(cmd)
        return {"sku": cmd.sku}

    return _app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def test_message_consumer_asgi_middleware(client: TestClient, caplog) -> None:
    caplog.set_level(logging.INFO)
    response = client.post("/orders", json={"sku": "sku-123"})
    response.raise_for_status()

    messages = [record.message for record in caplog.records]

    expected = any("sku-123" in message and "Consumed message" in message for message in messages)
    assert expected is True

import collections

import pytest

import compose


@pytest.fixture
def local_message_queue() -> compose.messaging.LocalMessageQueue:
    token = compose.messaging.event_store.set(collections.deque())
    yield compose.messaging.LocalMessageQueue()
    compose.messaging.event_store.reset(token)


class SomeEvent(compose.event.Event[compose.types.PyObjectId]):
    id: compose.types.PyObjectId = compose.field.IdField(default_factory=compose.types.PyObjectId)
    name: str


def test_push(local_message_queue: compose.messaging.LocalMessageQueue):
    message = compose.messaging.EventMessage(body=SomeEvent(name="some_event"))

    local_message_queue.push(message)

    assert compose.messaging.event_store.get().popleft() == message


def test_peek(local_message_queue: compose.messaging.LocalMessageQueue):
    message = compose.messaging.EventMessage(body=SomeEvent(name="some_event"))

    local_message_queue.push(message)

    assert local_message_queue.peek() == message


def test_delete(local_message_queue: compose.messaging.LocalMessageQueue):
    message = compose.messaging.EventMessage(body=SomeEvent(name="some_event"))

    local_message_queue.push(message)
    local_message_queue.delete(message)

    assert not compose.messaging.event_store.get()
    assert local_message_queue.peek() is None

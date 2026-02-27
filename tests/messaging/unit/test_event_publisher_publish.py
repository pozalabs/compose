import collections

import pendulum

import compose


class InMemoryMessageQueue(compose.messaging.MessageQueue):
    def __init__(self):
        self._queue = collections.deque()

    def push(self, message: compose.messaging.EventMessage) -> None:
        self._queue.append(message)

    def peek(self) -> compose.messaging.EventMessage | None:
        return self._queue[0] if self._queue else None

    def delete(self, message: compose.messaging.EventMessage) -> None:
        self._queue.remove(message)


class SomeEvent(compose.event.Event[compose.types.PyObjectId]):
    id: compose.types.PyObjectId = compose.field.PyObjectIdField(
        default_factory=compose.types.PyObjectId
    )


def test_publish():
    queue = InMemoryMessageQueue()
    publisher = compose.messaging.EventPublisher(queue)
    evt = SomeEvent(
        id=compose.types.PyObjectId(b"test-evt-001"),
        published_at=pendulum.datetime(2023, 12, 1),
    )

    publisher.publish(evt)

    assert queue.peek() == compose.messaging.EventMessage(body=evt)

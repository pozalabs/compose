import logging
from typing import Protocol

from ..event import Event
from .model import EventMessage


class MessagePushable(Protocol):
    def push(self, message: EventMessage) -> None: ...


logger = logging.getLogger("compose")


class EventPublisher:
    def __init__(self, message_queue: MessagePushable):
        self.message_queue = message_queue

    def publish(self, evt: Event) -> None:
        self.message_queue.push(EventMessage(body=evt))

        logger.info(f"Published event: {evt.__class__.__name__}")
        logger.debug(f"Event: {evt.model_dump(mode='json')}")

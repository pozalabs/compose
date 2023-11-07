import asyncio

from . import model
from .messagebus import MessageBus
from .queue import MessageQueue


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

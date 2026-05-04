import abc

from ..model import EventMessage


class MessageQueue[M: EventMessage = EventMessage](abc.ABC):
    @abc.abstractmethod
    def push(self, message: EventMessage) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def peek(self) -> M | None:
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, message: M) -> None:
        raise NotImplementedError

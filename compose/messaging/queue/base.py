import abc

from .. import model


class MessageQueue[M: model.EventMessage = model.EventMessage](abc.ABC):
    @abc.abstractmethod
    def push(self, message: model.EventMessage) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def peek(self) -> M | None:
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, message: M) -> None:
        raise NotImplementedError

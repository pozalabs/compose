import abc
import functools
from typing import Generic, TypeVar

from ..uow import MongoUnitOfWork

T = TypeVar("T")
R = TypeVar("R")


class MongoTransactionHandler(abc.ABC, Generic[T, R]):
    def __init__(self, uow: MongoUnitOfWork):
        self.uow = uow

    def handle(self, message: T, /) -> R:
        return self.uow.with_transaction(functools.partial(self.handle_in_transaction, message))

    def handle_in_transaction(self, message: T) -> R:
        raise NotImplementedError

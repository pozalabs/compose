import functools
from collections.abc import Callable
from typing import TypeVar

from pymongo.client_session import ClientSession, SessionOptions, TransactionOptions

from ..utils import unordered_partial

T = TypeVar("T")


class MongoUnitOfWork:
    def __init__(self, session_factory: Callable[..., ClientSession]):
        self.session_factory = session_factory

    def with_transaction(
        self,
        callback: Callable[[ClientSession], T],
        *,
        session_options: SessionOptions | None = None,
        transaction_options: TransactionOptions | None = None,
    ) -> T:
        session_options = session_options or SessionOptions()
        transaction_options = transaction_options or TransactionOptions()

        with self.session_factory(
            causal_consistency=session_options.causal_consistency,
            default_transaction_options=session_options.default_transaction_options,
            snapshot=session_options.snapshot,
        ) as session:
            result = session.with_transaction(
                callback=unordered_partial(p=functools.partial(callback), t=ClientSession),
                read_concern=transaction_options.read_concern,
                write_concern=transaction_options.write_concern,
                read_preference=transaction_options.read_preference,
                max_commit_time_ms=transaction_options.max_commit_time_ms,
            )

        return result

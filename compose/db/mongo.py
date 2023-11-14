from collections.abc import Callable
from typing import TypeAlias, TypeVar

from pymongo import WriteConcern
from pymongo.client_session import ClientSession
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import Nearest, Primary, PrimaryPreferred, SecondaryPreferred

T = TypeVar("T")
ServerMode: TypeAlias = Primary | PrimaryPreferred | SecondaryPreferred | Nearest


class MongoUnitOfWork:
    def __init__(self, session_factory: Callable[..., ClientSession]):
        self.session_factory = session_factory

    def with_transaction(
        self,
        callback: Callable[[ClientSession], T],
        read_concern: ReadConcern | None = None,
        write_concern: WriteConcern | None = None,
        read_preference: ServerMode | None = None,
        max_commit_time_ms: int | None = None,
    ) -> T:
        with self.session_factory() as session:
            result = session.with_transaction(
                callback=callback,
                read_concern=read_concern,
                write_concern=write_concern,
                read_preference=read_preference,
                max_commit_time_ms=max_commit_time_ms,
            )

        return result

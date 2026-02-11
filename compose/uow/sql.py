import functools
from collections.abc import Callable
from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from ..utils import unordered_partial


class SQLUnitOfWork[T]:
    def __init__(self, session_factory: sessionmaker[Session]):
        self.session_factory = session_factory

    def with_transaction(self, callback: Callable[..., T], **kwargs: Any) -> T:
        with self.session_factory() as session:
            try:
                result = unordered_partial(
                    p=functools.partial(callback, **kwargs),
                    t=Session,
                )(session)
                session.commit()
                return result
            except Exception:
                session.rollback()
                raise


def sql_transactional[T](func: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        instance = args[0]

        if not hasattr(instance, "__dict__"):
            raise ValueError(f"`{instance.__class__.__name__}` does not have `__dict__` attribute")

        uow: SQLUnitOfWork | None = next(
            (t for t in instance.__dict__.values() if isinstance(t, SQLUnitOfWork)),
            None,
        )
        if uow is None:
            raise ValueError(
                f"`{instance.__class__.__name__}` does not have `{SQLUnitOfWork.__name__}` attribute"
            )

        return uow.with_transaction(functools.partial(func, *args, **kwargs))

    return wrapper

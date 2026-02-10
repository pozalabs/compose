from __future__ import annotations

from typing import Any, overload

from pymongo.client_session import ClientSession

from ..entity import Entity
from .mongo import MongoRepository


class _Finder:
    def __init__(self, field: str) -> None:
        self._field = field

    @overload
    def __get__[T: Entity](self, obj: None, objtype: type[MongoRepository[T]]) -> _Finder: ...

    @overload
    def __get__[T: Entity](
        self, obj: MongoRepository[T], objtype: type[MongoRepository[T]]
    ) -> _BoundFinder[T]: ...

    def __get__[T: Entity](
        self, obj: MongoRepository[T] | None, objtype: type[MongoRepository[T]]
    ) -> _Finder | _BoundFinder[T]:
        if obj is None:
            return self
        return _BoundFinder(obj, self._field)


class _BoundFinder[T: Entity]:
    def __init__(self, repo: MongoRepository[T], field: str) -> None:
        self._repo = repo
        self._field = field

    def __call__(self, value: Any, *, session: ClientSession | None = None) -> T | None:
        return self._repo.find_by({self._field: value}, session=session)


class _Lister:
    def __init__(self, field: str) -> None:
        self._field = field

    @overload
    def __get__[T: Entity](self, obj: None, objtype: type[MongoRepository[T]]) -> _Lister: ...

    @overload
    def __get__[T: Entity](
        self, obj: MongoRepository[T], objtype: type[MongoRepository[T]]
    ) -> _BoundLister[T]: ...

    def __get__[T: Entity](
        self, obj: MongoRepository[T] | None, objtype: type[MongoRepository[T]]
    ) -> _Lister | _BoundLister[T]:
        if obj is None:
            return self
        return _BoundLister(obj, self._field)


class _BoundLister[T: Entity]:
    def __init__(self, repo: MongoRepository[T], field: str) -> None:
        self._repo = repo
        self._field = field

    def __call__(
        self,
        value: Any,
        *,
        sort: list[tuple[str, int]] | None = None,
        session: ClientSession | None = None,
    ) -> list[T]:
        return self._repo.list_by({self._field: value}, sort=sort, session=session)


def finder(field: str) -> _Finder:
    return _Finder(field)


def lister(field: str) -> _Lister:
    return _Lister(field)

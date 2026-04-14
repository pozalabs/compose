from __future__ import annotations

import functools
from typing import Any, ClassVar, Self, get_args, get_origin, overload

import pendulum
import pymongo
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import UpdateResult

from .. import types
from ..entity import Entity
from ..query.mongo import MongoPaginationQuery, MongoQuery
from .base import BaseRepository


class MongoDocument(dict[str, Any]):
    @classmethod
    def from_entity(cls, entity: Entity, **kwargs: Any) -> Self:
        return cls(
            entity.model_dump(
                by_alias=True,
                **{key: value for key, value in kwargs.items() if key not in {"by_alias"}},
            )
        )


class MongoRepository[T: Entity](BaseRepository):
    """
    `MongoRepository` 추상 클래스

    상속 인자:
        `session_requirement`: `MongoRepository` 상속 시 `session_requirement` 인자를 통해
        `session` 인자 선언 여부를 검사할 수 있습니다. 프로덕션에서는 `session_requirement`를
        `SessionRequirement.REQUIRED`로 설정하는 것을 권장합니다.

        ```python
        class UserRepository(
            MongoRepository[User],
            session_requirement=SessionRequirement.REQUIRED,
        ):
            ...
        ```

    """

    __collection_name__: ClassVar[str] = ""
    __indexes__: ClassVar[list[pymongo.IndexModel] | None] = None

    def __init__(self, collection: Collection):
        self.collection = collection

    @classmethod
    def create(cls, database: Database, **kwargs) -> Self:
        collection = database.get_collection(cls.__collection_name__, **kwargs)
        return cls(collection=collection)

    def ensure_indexes(self) -> None:
        if self.__indexes__ is not None:
            self.collection.create_indexes(self.__indexes__)

    def find_by_id(
        self,
        entity_id: types.PyObjectId,
        session: ClientSession | None = None,
        **kwargs,
    ) -> T | None:
        return self.find_by({"_id": entity_id}, session=session, **kwargs)

    @overload
    def find_by(
        self,
        filter_: dict[str, Any],
        *,
        projection: None = None,
        session: ClientSession | None = None,
        **kwargs,
    ) -> T | None: ...

    @overload
    def find_by(
        self,
        filter_: dict[str, Any],
        *,
        projection: dict[str, Any],
        session: ClientSession | None = None,
        **kwargs,
    ) -> dict[str, Any] | None: ...

    def find_by(
        self,
        filter_: dict[str, Any],
        *,
        projection: dict[str, Any] | None = None,
        session: ClientSession | None = None,
        **kwargs,
    ) -> T | dict[str, Any] | None:
        validate_to_entity = projection is None
        query_result = self.collection.find_one(
            filter=filter_,
            session=session,
            **kwargs,
        )
        if query_result is None:
            return None

        return (
            self._entity_type.model_validate(query_result) if validate_to_entity else query_result
        )

    def find_by_query(
        self, qry: MongoQuery, session: ClientSession | None = None, **kwargs
    ) -> dict[str, Any] | None:
        query_result = self.collection.aggregate(qry.to_query(), session=session, **kwargs)
        return next(query_result, None)

    @overload
    def list_by(
        self,
        filter_: dict[str, Any],
        *,
        projection: None = None,
        sort: list[tuple[str, int]] | None = None,
        session: ClientSession | None = None,
        **kwargs,
    ) -> list[T]: ...

    @overload
    def list_by(
        self,
        filter_: dict[str, Any],
        *,
        projection: dict[str, Any],
        sort: list[tuple[str, int]] | None = None,
        session: ClientSession | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]: ...

    def list_by(
        self,
        filter_: dict[str, Any],
        *,
        projection: dict[str, Any] | None = None,
        sort: list[tuple[str, int]] | None = None,
        session: ClientSession | None = None,
        **kwargs,
    ) -> list[T] | list[dict[str, Any]]:
        validate_to_entity = projection is None
        query_result = self.collection.find(
            filter=filter_,
            projection=projection,
            sort=sort,
            session=session,
            **kwargs,
        )
        return (
            [self._entity_type.model_validate(item) for item in query_result]
            if validate_to_entity
            else list(query_result)
        )

    def list_by_query(
        self, qry: MongoQuery, session: ClientSession | None = None, **kwargs
    ) -> list[dict[str, Any]]:
        query_result = self.collection.aggregate(qry.to_query(), session=session, **kwargs)
        return list(query_result)

    def add(self, entity: T, session: ClientSession | None = None, **kwargs) -> None:
        self.collection.insert_one(MongoDocument.from_entity(entity), session=session, **kwargs)

    def add_many(self, entities: list[T], session: ClientSession | None = None, **kwargs) -> None:
        self.collection.insert_many(
            [MongoDocument.from_entity(entity) for entity in entities], session=session, **kwargs
        )

    def update(self, entity: T, session: ClientSession | None = None, **kwargs) -> None:
        document = MongoDocument.from_entity(entity)
        update_result = self.collection.update_one(
            {"_id": entity.id},
            {"$set": document},
            session=session,
            **kwargs,
        )

        self.on_update(
            update_result=update_result,
            entity=entity,
            session=session,
            **kwargs,
        )

    def on_update(
        self,
        update_result: UpdateResult,
        entity: T,
        session: ClientSession | None = None,
        **kwargs,
    ) -> None:
        if not update_result.modified_count:
            return

        if getattr(entity, "updated_at") is None:
            return

        self.collection.update_one(
            {"_id": entity.id},
            {"$set": {"updated_at": pendulum.DateTime.utcnow()}},
            session=session,
            **kwargs,
        )

    def update_many(
        self, entities: list[T], session: ClientSession | None = None, **kwargs
    ) -> None:
        for entity in entities:
            self.update(entity=entity, session=session, **kwargs)

    def delete(
        self, entity_id: types.PyObjectId, session: ClientSession | None = None, **kwargs
    ) -> None:
        self.collection.delete_one({"_id": entity_id}, session=session, **kwargs)

    def paginate[R](
        self, qry: MongoPaginationQuery[R], session: ClientSession | None = None, **kwargs
    ) -> R:
        query_result = self.collection.aggregate(qry.to_query(), session=session, **kwargs)
        return qry.to_result(next(query_result, None))

    @functools.cached_property
    def _entity_type(self) -> T:
        orig_base = next(
            (base for base in self.__class__.__orig_bases__ if get_origin(base) is MongoRepository),  # type: ignore[missing-attribute]
            None,
        )
        if orig_base is None:
            raise ValueError(
                f"{self.__class__.__name__} must inherit MongoRepository[T] with explicit type parameter"
            )

        return get_args(orig_base)[0]


def setup_indexes(*repositories: *tuple[MongoRepository, ...]) -> None:
    for repository in repositories:
        repository.ensure_indexes()

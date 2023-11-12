from __future__ import annotations

from typing import Any, ClassVar, Generic, Optional, TypeVar, get_args

import pymongo
from pymongo import UpdateOne
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.database import Database

from .. import types
from ..entity import Entity
from ..pagination import Pagination
from ..query.mongo import MongoFilterQuery, MongoQuery
from . import base

EntityType = TypeVar("EntityType", bound=Entity)


def entity_to_mongo_schema(entity: EntityType, **kwargs) -> dict[str, Any]:
    default_kwargs = {"by_alias": True}
    return entity.model_dump(**(default_kwargs | kwargs))


class MongoRepository(base.BaseRepository, Generic[EntityType]):
    __collection_name__: ClassVar[str] = ""
    __indexes__: ClassVar[Optional[list[pymongo.IndexModel]]] = None

    def __init__(self, collection: Collection):
        self.collection = collection

    @classmethod
    def create(cls, database: Database, **kwargs) -> MongoRepository:
        collection = database.get_collection(cls.__collection_name__, **kwargs)
        if cls.__indexes__ is not None:
            collection.create_indexes(cls.__indexes__)
        return cls(collection)

    def find_by_id(
        self,
        entity_id: types.PyObjectId,
        session: ClientSession | None = None,
        **kwargs,
    ) -> Optional[EntityType]:
        return self.find_by({"_id": entity_id}, session=session, **kwargs)

    def find_by(
        self, filter_: dict[str, Any], session: ClientSession | None = None, **kwargs
    ) -> Optional[EntityType]:
        """https://stackoverflow.com/a/73746554/9331155"""
        entity_type: EntityType = get_args(self.__class__.__orig_bases__[0])[0]  # type: ignore
        result = self.collection.find_one(filter=filter_, session=session, **kwargs)
        return result and entity_type.model_validate(result)

    def find_by_query(
        self, qry: MongoQuery, session: ClientSession | None = None, **kwargs
    ) -> Optional[dict[str, Any]]:
        query_result = self.collection.aggregate(qry.to_query(), session=session, **kwargs)
        return next(query_result, None)

    def list_by_query(
        self, qry: MongoQuery, session: ClientSession | None = None, **kwargs
    ) -> list[dict[str, Any]]:
        query_result = self.collection.aggregate(qry.to_query(), session=session, **kwargs)
        return list(query_result)

    def add(self, entity: EntityType, session: ClientSession | None = None, **kwargs) -> None:
        self.collection.insert_one(entity_to_mongo_schema(entity), session=session, **kwargs)

    def add_many(
        self, entities: list[EntityType], session: ClientSession | None = None, **kwargs
    ) -> None:
        self.collection.insert_many(
            [entity_to_mongo_schema(entity) for entity in entities], session=session, **kwargs
        )

    def update(self, entity: EntityType, session: ClientSession | None = None, **kwargs) -> None:
        self.collection.update_one(
            {"_id": entity.id},
            {"$set": entity_to_mongo_schema(entity)},
            session=session,
            **kwargs,
        )

    def update_many(
        self, entities: list[EntityType], session: ClientSession | None = None, **kwargs
    ) -> None:
        self.collection.bulk_write(
            requests=[
                UpdateOne({"_id": entity.id}, {"$set": entity_to_mongo_schema(entity)})
                for entity in entities
            ],
            session=session,
            **kwargs,
        )

    def delete(
        self, entity_id: types.PyObjectId, session: ClientSession | None = None, **kwargs
    ) -> None:
        self.collection.delete_one({"_id": entity_id}, session=session, **kwargs)

    def execute_raw(self, operation: str, **operation_kwargs) -> Any:
        op = getattr(self.collection, operation, None)
        if op is None:
            raise ValueError(f"Unknown operation on collection: {operation}")
        return op(**operation_kwargs)

    def filter(
        self, qry: MongoFilterQuery, session: ClientSession | None = None, **kwargs
    ) -> Pagination:
        query_result = self.collection.aggregate(qry.to_query(), session=session, **kwargs)
        if (unwrapped := next(query_result, None)) is None:
            raise ValueError(f"{qry.__class__.__name__} returned nothing")

        return Pagination(
            total=(unwrapped["metadata"][0]["total"] if unwrapped["metadata"] else 0),
            items=unwrapped["items"],
            page=qry.page,
            per_page=qry.per_page,
        )

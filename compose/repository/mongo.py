from __future__ import annotations

import enum
import inspect
from typing import Any, ClassVar, Generic, TypeVar, get_args, get_type_hints

import pendulum
import pymongo
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import UpdateResult

from .. import compat, types
from ..entity import Entity
from ..pagination import Pagination
from ..query.mongo import MongoFilterQuery, MongoQuery
from . import base

EntityType = TypeVar("EntityType", bound=Entity)


class SessionRequirement(str, enum.Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"


def entity_to_mongo_schema(entity: EntityType, **kwargs) -> dict[str, Any]:
    default_kwargs = {"by_alias": True}
    return compat.model_dump(entity, **(default_kwargs | kwargs))


class MongoRepository(base.BaseRepository, Generic[EntityType]):
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

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        cls._validate_session_requirement(
            kwargs.get("session_requirement", SessionRequirement.OPTIONAL)
        )

    @classmethod
    def _validate_session_requirement(cls, requirement: SessionRequirement) -> None:
        if requirement == SessionRequirement.OPTIONAL:
            return

        error_message = "Method {} does not have a session argument"
        # 클래스 자체를 검사하기 때문에 `inspect.ismethod`를 사용하면 인스턴스 메서드가 아니라 클래스메서드를 리턴
        for name, member in inspect.getmembers(cls, predicate=inspect.isfunction):
            if name.startswith("__"):
                continue

            # https://stackoverflow.com/q/72510518
            # `inspect.get_annotations`를 사용하면 `__future__.annotations`을 사용했을 때에는 문자열을,
            # 그렇지 않은 경우에는 `type`을 리턴함. `__future__.annotations` 사용 여부에 관계 없이
            # 항상 `type`을 얻기 위해 `typing.get_type_hints` 사용
            if (type_hints := get_type_hints(member).get("session")) is None:
                raise ValueError(error_message.format(name))

            if not (args := get_args(type_hints)):
                raise ValueError(error_message.format(name))

            session = args[0]
            if session is not ClientSession:
                raise ValueError(error_message.format(name))

    @classmethod
    def create(cls, database: Database, **kwargs) -> MongoRepository:
        collection = database.get_collection(cls.__collection_name__, **kwargs)
        if cls.__indexes__ is not None:
            collection.create_indexes(cls.__indexes__)

        return cls(collection=collection)

    def find_by_id(
        self,
        entity_id: types.PyObjectId,
        session: ClientSession | None = None,
        **kwargs,
    ) -> EntityType | None:
        return self.find_by({"_id": entity_id}, session=session, **kwargs)

    def find_by(
        self, filter_: dict[str, Any], session: ClientSession | None = None, **kwargs
    ) -> EntityType | None:
        """https://stackoverflow.com/a/73746554/9331155"""
        entity_type: EntityType = get_args(self.__class__.__orig_bases__[0])[0]  # type: ignore
        result = self.collection.find_one(filter=filter_, session=session, **kwargs)
        return result and compat.model_validate(entity_type, result)

    def find_by_query(
        self, qry: MongoQuery, session: ClientSession | None = None, **kwargs
    ) -> dict[str, Any] | None:
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
        schema = entity_to_mongo_schema(entity)
        update_result = self.collection.update_one(
            {"_id": entity.id},
            {"$set": schema},
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
        entity: EntityType,
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
        self, entities: list[EntityType], session: ClientSession | None = None, **kwargs
    ) -> None:
        for entity in entities:
            self.update(entity=entity, session=session, **kwargs)

    def delete(
        self, entity_id: types.PyObjectId, session: ClientSession | None = None, **kwargs
    ) -> None:
        self.collection.delete_one({"_id": entity_id}, session=session, **kwargs)

    def execute_raw(
        self,
        operation: str,
        session: ClientSession | None = None,
        **operation_kwargs,
    ) -> Any:
        op = getattr(self.collection, operation, None)
        if op is None:
            raise ValueError(f"Unknown operation on collection: {operation}")
        return op(session=session, **operation_kwargs)

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

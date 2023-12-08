from __future__ import annotations

import enum
import inspect
from collections.abc import Callable
from typing import Annotated, Any, ClassVar, Generic, Optional, TypeVar, get_args, get_type_hints

import pendulum
import pymongo
from pydantic import Field
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.database import Database

from .. import compat, container, types
from ..entity import Entity
from ..pagination import Pagination
from ..query.mongo import MongoFilterQuery, MongoQuery
from . import base

EntityType = TypeVar("EntityType", bound=Entity)


if compat.IS_PYDANTIC_V2:
    from pydantic import AfterValidator

    def validate_unique_spec_keys(
        specs: list[tuple[str, Callable[[], Any]] | Any]
    ) -> list[tuple[str, Callable[[], Any]] | Any]:
        spec_keys = {spec[0] for spec in specs}
        assert len(spec_keys) == len(specs), "Spec keys must be unique"
        return specs

    OnUpdateSpecs = Annotated[
        list[tuple[str, Callable[[], Any]] | Any],
        AfterValidator(validate_unique_spec_keys),
    ]
else:
    OnUpdateSpecs = list[tuple[str, Callable[[], Any]] | Any]


class SessionRequirement(str, enum.Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"


def entity_to_mongo_schema(entity: EntityType, **kwargs) -> dict[str, Any]:
    default_kwargs = {"by_alias": True}
    return compat.model_dump(entity, **(default_kwargs | kwargs))


class OnUpdate(container.BaseModel):
    specs: OnUpdateSpecs = Field(
        default_factory=lambda: [("updated_at", pendulum.DateTime.utcnow)],
    )

    def to_updates(self, schema: dict[str, Any]) -> dict[str, Any]:
        specs = self.specs or [("updated_at", pendulum.DateTime.utcnow)]
        return {
            field: value() if isinstance(value, Callable) else value
            for field, value in specs
            if schema.get(field) is not None
        }

    if not compat.IS_PYDANTIC_V2:
        from pydantic import validator

        @validator("specs")
        def validate_unique_spec_keys(cls, specs: list[OnUpdateSpecs]) -> list[OnUpdateSpecs]:
            spec_keys = {spec[0] for spec in specs}
            if len(spec_keys) != len(specs):
                raise ValueError("Spec keys must be unique")

            return specs


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
    __indexes__: ClassVar[Optional[list[pymongo.IndexModel]]] = None

    def __init__(self, collection: Collection, on_update: OnUpdate | None = None):
        self.collection = collection
        self.on_update = on_update or OnUpdate()

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
    def create(
        cls,
        database: Database,
        on_update: OnUpdate | None = None,
        **kwargs,
    ) -> MongoRepository:
        collection = database.get_collection(cls.__collection_name__, **kwargs)
        if cls.__indexes__ is not None:
            collection.create_indexes(cls.__indexes__)
        return cls(collection=collection, on_update=on_update)

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
        return result and compat.model_validate(entity_type, result)

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
        schema = entity_to_mongo_schema(entity)
        update_result = self.collection.update_one(
            {"_id": entity.id},
            {"$set": schema},
            session=session,
            **kwargs,
        )
        if not update_result.modified_count:
            return

        if self.on_update is None or not (updates := self.on_update.to_updates(schema)):
            return

        self.collection.update_one({"_id": entity.id}, updates, session=session, **kwargs)

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

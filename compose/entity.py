import uuid
from typing import Any, ClassVar, Generic

from pydantic import Field

from . import field, model
from .typing import IdT
from .utils import uuid7


class Entity(model.TimeStampedModel, Generic[IdT]):
    id: IdT

    updatable_fields: ClassVar[set[str]] = set()

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        fields = set(cls.model_fields.keys())
        if diff := set(cls.updatable_fields) - fields:
            raise ValueError(f"`updatable_fields` must be subset of {fields}, but got {diff}")

    def update(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if key not in self.updatable_fields:
                continue

            setattr(self, key, value)


try:
    from .types import PyObjectId

    class MongoEntity(Entity[PyObjectId]):
        id: PyObjectId = field.PyObjectIdField(default_factory=PyObjectId)

except ImportError:
    pass

try:
    from sqlalchemy.orm import Session  # noqa: F401

    class SQLEntity(Entity[uuid.UUID]):
        id: uuid.UUID = Field(default_factory=uuid7)

except ImportError:
    pass

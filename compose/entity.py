import uuid
from typing import Generic

from pydantic import Field

from . import field, model
from .typing import IdT
from .utils import uuid7


class Entity(model.TimeStampedModel, Generic[IdT]):
    id: IdT


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

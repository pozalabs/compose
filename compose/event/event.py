from typing import Generic, TypeVar

from .. import container, field, types

IdT = TypeVar("IdT")


class Event(container.BaseModel, Generic[IdT]):
    id: IdT
    published_at: types.DateTime = field.DateTimeField()


try:
    from ..types import PyObjectId

    class MongoEvent(Event[PyObjectId]):
        id: PyObjectId = field.IdField(default_factory=PyObjectId)

except ImportError:
    pass

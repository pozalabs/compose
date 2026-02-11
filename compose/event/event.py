from typing import Generic

from .. import container, field, types
from ..typing import IdT


class Event(container.BaseModel, Generic[IdT]):
    id: IdT
    published_at: types.DateTime = field.DateTimeField()

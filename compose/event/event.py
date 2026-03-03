from typing import Generic

from .. import field, model, types
from ..typing import IdT


class Event(model.BaseModel, Generic[IdT]):
    id: IdT
    published_at: types.DateTime = field.DateTimeField()

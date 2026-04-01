import uuid

from pydantic import Field

from .. import field, model, types


class Event(model.BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    published_at: types.DateTime = field.DateTimeField()

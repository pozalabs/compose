from .. import container, field, types


class Event(container.BaseModel):
    id: types.PyObjectId = field.IdField()
    published_at: types.DateTime = field.DateTimeField()

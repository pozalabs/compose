from .. import container
from . import extra


class Schema(container.BaseModel):
    class Config:
        schema_extra = extra.schema_by_field_name()


class TimeStampedSchema(container.TimeStampedModel, Schema):
    ...

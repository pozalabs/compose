from typing import Generic, TypeVar

from pydantic.generics import GenericModel

from .. import container
from . import extra

ListItem = TypeVar("ListItem")


class Schema(container.BaseModel):
    class Config:
        schema_extra = extra.schema_by_field_name()


class TimeStampedSchema(container.TimeStampedModel, Schema):
    ...


class ListSchema(Schema, GenericModel, Generic[ListItem]):
    total: int
    items: list[ListItem]

import datetime
from typing import Any

import bson
from pydantic import BaseModel as PydanticBaseModel

from . import field


class BaseModel(PydanticBaseModel):
    class Config:
        json_encoders = {bson.ObjectId: str}
        allow_population_by_field_name = True
        validate_assignment = True


class TimeStampedModel(BaseModel):
    created_at: datetime.datetime = field.DateTimeField()
    updated_at: datetime.datetime = field.DateTimeField()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        created_at_field = cls.__fields__.pop("created_at")
        updated_at_field = cls.__fields__.pop("updated_at")
        cls.__fields__ |= dict(created_at=created_at_field, updated_at=updated_at_field)

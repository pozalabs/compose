import bson
from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    class Config:
        json_encoders = {bson.ObjectId: str}
        allow_population_by_field_name = True
        validate_assignment = True

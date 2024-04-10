import compose


class User(compose.schema.TimeStampedSchema):
    id: compose.types.PyObjectId
    name: str

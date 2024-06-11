import compose


class User(compose.schema.TimeStampedSchema):
    id: compose.types.PyObjectId = compose.field.IdField()
    name: str

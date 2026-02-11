import compose


class User(compose.schema.TimeStampedSchema):
    id: int
    name: str

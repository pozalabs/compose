import uuid

import compose


class User(compose.schema.TimeStampedSchema):
    id: uuid.UUID
    name: str

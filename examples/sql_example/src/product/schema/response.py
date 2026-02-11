import compose


class Product(compose.schema.TimeStampedSchema):
    id: int
    name: str
    price: int

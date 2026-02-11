import compose


class Product(compose.entity.SQLEntity):
    name: str
    price: int

    updatable_fields = {"name", "price"}

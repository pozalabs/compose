import compose


class User(compose.entity.SQLEntity):
    name: str
    email: str

    updatable_fields = {"name", "email"}

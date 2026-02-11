import compose


class User(compose.entity.MongoEntity):
    name: str
    email: str

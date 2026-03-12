import compose
from src.user.domain import model


class UserRepository(compose.repository.MongoRepository[model.User]):
    __collection_name__ = "user"

    def find_by_name(self, name: str) -> model.User | None:
        return self.find_by({"name": name})

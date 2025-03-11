import compose.repository
from src.user.domain import model


class UserRepository(compose.repository.MongoRepository[model.User]):
    __collection_name__ = "user"

    def find_by_name(self, name: str) -> model.User | None:
        return self.find_by({"name": name})

    def all(self) -> list[model.User]:
        return [model.User.model_validate(**item) for item in self.collection.find()]

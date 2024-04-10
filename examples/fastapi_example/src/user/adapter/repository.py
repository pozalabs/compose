from src.user.domain.model import User

USER_DATA = []


class UserRepository:
    def __init__(self):
        self._data = USER_DATA

    def add(self, user: User) -> None:
        self._data.append(user)

    def find_by_name(self, name: str) -> User | None:
        return next((user for user in self._data if user.name == name), None)

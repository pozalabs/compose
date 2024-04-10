import compose.exceptions
from src.user import schema
from src.user.adapter.repository import UserRepository
from src.user.domain import command, model


class AddUserHandler:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def handle(self, cmd: command.AddUser) -> schema.User:
        if (user := self.user_repository.find_by_name(cmd.name)) is not None:
            raise compose.exceptions.DomainValidationError(f"User {user.name} already exists")

        user = model.User(name=cmd.name)
        self.user_repository.add(user)

        return schema.User.model_validate(user.encode())

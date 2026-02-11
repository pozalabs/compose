from sqlalchemy.orm import Session
from src.user.adapter.repository import UserRepository
from src.user.domain import command, model
from src.user.schema import response

import compose
from compose.uow.sql import SQLUnitOfWork, sql_transactional


class AddUserHandler:
    def __init__(self, user_repository: UserRepository, uow: SQLUnitOfWork):
        self.user_repository = user_repository
        self.uow = uow

    @sql_transactional
    def handle(self, cmd: command.AddUser, session: Session) -> response.User:
        if self.user_repository.find_by_name(cmd.name, session) is not None:
            raise compose.exceptions.DomainValidationError(f"User {cmd.name} already exists")

        user = model.User(name=cmd.name, email=cmd.email)
        self.user_repository.add(user, session)
        return response.User.model_validate(user.model_dump(mode="json"))

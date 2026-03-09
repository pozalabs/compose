from dishka import Provider, Scope, provide
from pymongo.database import Database

from src.user.adapter.repository import UserRepository
from src.user.service.command_handler import AddUserHandler


class UserProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def user_repository(self, database: Database) -> UserRepository:
        return UserRepository.create(database)

    @provide
    def add_user_handler(self, user_repository: UserRepository) -> AddUserHandler:
        return AddUserHandler(user_repository=user_repository)

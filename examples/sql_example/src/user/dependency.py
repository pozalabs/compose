from dependency_injector import containers, providers
from src.user import service
from src.user.adapter.repository import UserRepository

from compose.uow.sql import SQLUnitOfWork


class AdapterContainer(containers.DeclarativeContainer):
    user_repository = providers.Factory(UserRepository)


class ServiceContainer(containers.DeclarativeContainer):
    adapter = providers.DependenciesContainer()
    session_factory = providers.Dependency()

    add_user_handler = providers.Factory(
        service.AddUserHandler,
        user_repository=adapter.user_repository,
        uow=providers.Factory(SQLUnitOfWork, session_factory=session_factory),
    )


class UserContainer(containers.DeclarativeContainer):
    session_factory = providers.Dependency()

    adapter = providers.Container(AdapterContainer)
    service = providers.Container(
        ServiceContainer, adapter=adapter, session_factory=session_factory
    )

from dependency_injector import containers, providers

from src.user import service
from src.user.adapter.repository import UserRepository


class AdapterContainer(containers.DeclarativeContainer):
    database = providers.Dependency()

    user_repository = providers.Factory(UserRepository.create, database=database)


class ServiceContainer(containers.DeclarativeContainer):
    adapter = providers.DependenciesContainer()

    add_user_handler = providers.Factory(
        service.AddUserHandler,
        user_repository=adapter.user_repository,
    )


class UserContainer(containers.DeclarativeContainer):
    database = providers.Dependency()

    adapter = providers.Container(AdapterContainer, database=database)
    service = providers.Container(ServiceContainer, adapter=adapter)

from dependency_injector import containers, providers

from src.user import service
from src.user.adapter.repository import UserRepository


class AdapterContainer(containers.DeclarativeContainer):
    user_repository = providers.Factory(UserRepository)


class ServiceContainer(containers.DeclarativeContainer):
    adapter = providers.DependenciesContainer()

    add_user_handler = providers.Factory(
        service.AddUserHandler,
        user_repository=adapter.user_repository,
    )


class UserContainer(containers.DeclarativeContainer):
    adapter = providers.Container(AdapterContainer)
    service = providers.Container(ServiceContainer, adapter=adapter)

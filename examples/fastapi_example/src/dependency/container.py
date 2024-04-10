from dependency_injector import providers

import compose
from src.user.dependency import UserContainer

PACKAGES = {
    "src.user",
}


class ApplicationContainer(compose.dependency.DeclarativeContainer):
    user = providers.Container(UserContainer)


wirer = compose.dependency.create_wirer(packages=PACKAGES)
provide = compose.dependency.create_provider(ApplicationContainer)

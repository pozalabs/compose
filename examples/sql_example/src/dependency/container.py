from dependency_injector import providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.user.dependency import UserContainer

import compose

PACKAGES = {
    "src.user",
}


class ApplicationContainer(compose.dependency.DeclarativeContainer):
    engine = providers.Singleton(create_engine, "sqlite:///users.db")
    session_factory = providers.Singleton(sessionmaker, bind=engine)

    user = providers.Container(UserContainer, session_factory=session_factory)


wirer = compose.dependency.create_wirer(packages=PACKAGES)
provide = compose.dependency.create_provider(ApplicationContainer)

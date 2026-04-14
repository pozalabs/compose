from dependency_injector import providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.user.dependency import UserContainer

from compose.di import dependency_injector as di

PACKAGES = {
    "src.user",
}


class ApplicationContainer(di.DeclarativeContainer):
    engine = providers.Singleton(create_engine, "sqlite:///users.db")
    session_factory = providers.Singleton(sessionmaker, bind=engine)

    user = providers.Container(UserContainer, session_factory=session_factory)


provide = di.create_provider(ApplicationContainer)

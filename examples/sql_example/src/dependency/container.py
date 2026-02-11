from dependency_injector import providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.product.dependency import ProductContainer

import compose

PACKAGES = {
    "src.product",
}


class ApplicationContainer(compose.dependency.DeclarativeContainer):
    engine = providers.Singleton(create_engine, "sqlite:///products.db")
    session_factory = providers.Singleton(sessionmaker, bind=engine)

    product = providers.Container(ProductContainer, session_factory=session_factory)


wirer = compose.dependency.create_wirer(packages=PACKAGES)
provide = compose.dependency.create_provider(ApplicationContainer)

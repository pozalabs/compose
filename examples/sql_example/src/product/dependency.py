from dependency_injector import containers, providers
from src.product import service
from src.product.adapter.repository import ProductRepository

from compose.uow.sql import SQLUnitOfWork


class AdapterContainer(containers.DeclarativeContainer):
    product_repository = providers.Factory(ProductRepository)


class ServiceContainer(containers.DeclarativeContainer):
    adapter = providers.DependenciesContainer()
    session_factory = providers.Dependency()

    add_product_handler = providers.Factory(
        service.AddProductHandler,
        product_repository=adapter.product_repository,
        uow=providers.Factory(SQLUnitOfWork, session_factory=session_factory),
    )


class ProductContainer(containers.DeclarativeContainer):
    session_factory = providers.Dependency()

    adapter = providers.Container(AdapterContainer)
    service = providers.Container(
        ServiceContainer, adapter=adapter, session_factory=session_factory
    )

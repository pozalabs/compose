from sqlalchemy.orm import Session
from src.product.adapter.repository import ProductRepository
from src.product.domain import command, model
from src.product.schema import response

import compose
from compose.uow.sql import SQLUnitOfWork, sql_transactional


class AddProductHandler:
    def __init__(self, product_repository: ProductRepository, uow: SQLUnitOfWork):
        self.product_repository = product_repository
        self.uow = uow

    @sql_transactional
    def handle(self, cmd: command.AddProduct, session: Session) -> response.Product:
        if self.product_repository.find_by_name(cmd.name, session) is not None:
            raise compose.exceptions.DomainValidationError(f"Product {cmd.name} already exists")

        product = model.Product(name=cmd.name, price=cmd.price)
        self.product_repository.add(product, session)
        return response.Product.model_validate(product.model_dump(mode="json"))

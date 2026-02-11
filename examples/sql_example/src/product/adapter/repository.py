from sqlalchemy.orm import Session
from src.product.adapter.table import products_table
from src.product.domain import model

import compose


class ProductRepository(compose.repository.SQLRepository[model.Product]):
    __table__ = products_table

    def find_by_name(self, name: str, session: Session) -> model.Product | None:
        return self.find_by({"name": name}, session)

from sqlalchemy.orm import Session
from src.user.adapter.table import users_table
from src.user.domain import model

import compose


class UserRepository(compose.repository.SQLRepository[model.User]):
    __table__ = users_table

    def find_by_name(self, name: str, session: Session) -> model.User | None:
        return self.find_by({"name": name}, session)

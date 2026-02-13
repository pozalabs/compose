from __future__ import annotations

import functools
from typing import Any, ClassVar, get_args, get_origin

import pendulum
from sqlalchemy import Table, delete, insert, select, update
from sqlalchemy.orm import Session

from ..entity import SQLEntity
from .base import BaseRepository


class SQLRepository[T: SQLEntity](BaseRepository):
    __table__: ClassVar[Table]

    def find_by_id(self, entity_id: int, session: Session) -> T | None:
        return self.find_by({"id": entity_id}, session=session)

    def find_by(self, filter_: dict[str, Any], session: Session) -> T | None:
        table = self.__table__
        stmt = select(table).filter_by(**filter_)
        row = session.execute(stmt).mappings().first()
        if row is None:
            return None

        return self._entity_type.model_validate(dict(row))

    def list_by(
        self,
        filter_: dict[str, Any],
        session: Session,
        *,
        sort: list[tuple[str, int]] | None = None,
    ) -> list[T]:
        table = self.__table__
        stmt = select(table).filter_by(**filter_)

        if sort is not None:
            order_clauses = [
                table.c[col].asc() if direction == 1 else table.c[col].desc()
                for col, direction in sort
            ]
            stmt = stmt.order_by(*order_clauses)

        rows = session.execute(stmt).mappings().all()
        return [self._entity_type.model_validate(dict(row)) for row in rows]

    def add(self, entity: T, session: Session) -> None:
        table = self.__table__
        row = self._to_row(entity)
        result = session.execute(insert(table).values(**row))
        entity.id = result.inserted_primary_key[0]

    def add_many(self, entities: list[T], session: Session) -> None:
        table = self.__table__
        rows = [self._to_row(entity) for entity in entities]
        session.execute(insert(table), rows)

    def update(self, entity: T, session: Session) -> None:
        table = self.__table__
        row = entity.model_dump(mode="json", exclude={"id"})

        if "updated_at" in row:
            now = pendulum.DateTime.utcnow()
            entity.updated_at = now
            row["updated_at"] = now.isoformat()

        session.execute(update(table).where(table.c.id == entity.id).values(**row))

    def delete(self, entity_id: int, session: Session) -> None:
        table = self.__table__
        session.execute(delete(table).where(table.c.id == entity_id))

    @functools.cached_property
    def _entity_type(self) -> type[T]:
        orig_base = next(
            (base for base in self.__class__.__orig_bases__ if get_origin(base) is SQLRepository),
            None,
        )
        if orig_base is None:
            raise ValueError(
                f"{self.__class__.__name__} must inherit SQLRepository[T] with explicit type parameter"
            )

        return get_args(orig_base)[0]

    @staticmethod
    def _to_row(entity: T) -> dict[str, Any]:
        row = entity.model_dump(mode="json")
        if row.get("id") is None:
            row.pop("id", None)
        return row

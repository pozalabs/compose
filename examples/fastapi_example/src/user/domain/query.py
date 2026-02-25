from typing import Any

from pydantic import Field

import compose
from compose.query.mongo import op


class ListUsers(compose.query.MongoOffsetPaginationQuery):
    name: str

    def to_query(self) -> list[dict[str, Any]]:
        return op.func.Pipeline(
            op.Match.and_(op.Eq.from_(name=self.name)),
            op.OffsetPagination(page=self.page, per_page=self.per_page),
        )


class UserCursor(op.Cursor):
    created_at: compose.types.DateTime
    id: compose.types.PyObjectId = Field(alias="_id")


class ListRecentUsers(compose.query.MongoCursorPaginationQuery):
    cursor: str | None = None

    def derive_cursor(self, last_item: dict[str, Any]) -> str:
        return UserCursor(
            created_at=last_item["created_at"],
            id=last_item["_id"],
        ).to_str()

    def to_query(self) -> list[dict[str, Any]]:
        sort = op.Sort(
            op.SortBy.desc("created_at"),
            op.SortBy.desc("_id"),
        )
        parsed_cursor = UserCursor.from_str(self.cursor) if self.cursor else None

        return op.CursorPagination(
            sort=sort,
            cursor=parsed_cursor,
            per_page=self.per_page,
        ).expression()

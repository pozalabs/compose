from typing import Any

import compose
from compose.query.mongo import op


class ListUsers(compose.query.MongoFilterQuery):
    name: str

    def to_query(self) -> list[dict[str, Any]]:
        return op.func.Pipeline(
            op.Match.and_(op.Eq.from_(name=self.name)),
            op.Pagination(),
        )

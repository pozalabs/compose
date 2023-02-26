from typing import Any, Optional

from pydantic import Field

from .. import base


class MongoQuery(base.Query):
    def to_query(self) -> list[dict[str, Any]]:
        ...


class MongoFilterQuery(MongoQuery):
    page: Optional[int] = Field(None, ge=1)
    per_page: Optional[int] = Field(None, ge=1)

    @property
    def can_paginate(self) -> bool:
        return self.page is not None and self.per_page is not None

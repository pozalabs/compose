from typing import Any

from pydantic import Field

from .. import container


class Query(container.BaseModel):
    def to_query(self) -> Any: ...


class OffsetPaginationQuery(Query):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1)

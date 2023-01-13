import abc
from typing import Any, Optional

from pydantic import conint

from ..base import Query


class MongoQuery(Query, abc.ABC):
    def to_query(self) -> list[dict[str, Any]]:
        ...


class MongoFilterQuery(MongoQuery):
    page: Optional[conint(gt=1)] = None
    per_page: Optional[conint(gt=1)] = None

    @property
    def can_paginate(self) -> bool:
        return self.page is not None and self.per_page is not None

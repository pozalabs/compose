import abc
from typing import Any

from .. import base


class MongoQuery(base.Query, abc.ABC):
    @abc.abstractmethod
    def to_query(self) -> list[dict[str, Any]]:
        raise NotImplementedError


class MongoFilterQuery(base.OffsetPaginationQuery, MongoQuery):
    @abc.abstractmethod
    def to_query(self) -> list[dict[str, Any]]:
        raise NotImplementedError


MongoOffsetFilterQuery = MongoFilterQuery

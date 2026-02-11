from .base import OffsetPaginationQuery, Query

__all__ = ["OffsetPaginationQuery", "Query"]

try:
    from .mongo.query import MongoFilterQuery, MongoOffsetFilterQuery, MongoQuery

    __all__ += ["MongoFilterQuery", "MongoOffsetFilterQuery", "MongoQuery"]
except ImportError:
    pass

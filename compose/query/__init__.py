from .base import OffsetPaginationQuery, Query

__all__ = ["OffsetPaginationQuery", "Query"]

try:
    from .mongo.query import (
        MongoCursorPaginationQuery,
        MongoOffsetPaginationQuery,
        MongoPaginationQuery,
        MongoQuery,
    )

    __all__ += [
        "MongoCursorPaginationQuery",
        "MongoOffsetPaginationQuery",
        "MongoPaginationQuery",
        "MongoQuery",
    ]
except ImportError:
    pass

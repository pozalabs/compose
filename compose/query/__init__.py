from .base import Query

__all__ = ["Query"]

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

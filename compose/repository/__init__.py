from .base import BaseRepository

__all__ = ["BaseRepository"]

try:
    from .mongo import MongoDocument, MongoRepository, setup_indexes
    from .shortcut import finder, lister

    __all__ += ["MongoDocument", "MongoRepository", "finder", "lister", "setup_indexes"]
except ImportError:
    pass

try:
    from .sql import SQLRepository

    __all__ += ["SQLRepository"]
except ImportError:
    pass

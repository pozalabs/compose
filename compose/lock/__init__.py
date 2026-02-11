from .exceptions import LockAcquisitionFailedError

__all__ = ["LockAcquisitionFailedError"]

try:
    from .mongo import MongoLock, MongoLockAcquirer

    __all__ += ["MongoLock", "MongoLockAcquirer"]
except ImportError:
    pass

from .event import Event

__all__ = ["Event"]

try:
    from .event import MongoEvent

    __all__ += ["MongoEvent"]
except ImportError:
    pass

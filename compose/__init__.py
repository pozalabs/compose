from . import compat, dependency

if compat.IS_PYDANTIC_V2:
    from . import command, entity, event, field, query, repository, schema, types
    from .container import BaseModel, TimeStampedModel
else:
    from .v1 import command, entity, event, field, query, repository, schema, types
    from .v1.container import BaseModel, TimeStampedModel

__all__ = [
    "BaseModel",
    "TimeStampedModel",
    "entity",
    "field",
    "schema",
    "repository",
    "query",
    "types",
    "command",
    "event",
    "dependency",
]

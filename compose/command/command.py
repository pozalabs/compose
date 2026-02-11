from typing import Generic, TypeVar

from pydantic import ConfigDict

from .. import container, schema

IdT = TypeVar("IdT")


class Command(container.BaseModel): ...


class UserCommand(Command, Generic[IdT]):
    user_id: IdT | None = None

    model_config = ConfigDict(json_schema_extra=schema.extra.schema_excludes("user_id"))

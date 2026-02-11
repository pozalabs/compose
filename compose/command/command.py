from typing import Generic

from pydantic import ConfigDict

from .. import container, schema
from ..typing import IdT


class Command(container.BaseModel): ...


class UserCommand(Command, Generic[IdT]):
    user_id: IdT | None = None

    model_config = ConfigDict(json_schema_extra=schema.extra.schema_excludes("user_id"))

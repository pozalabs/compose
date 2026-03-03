from typing import Any

from .. import model


class Query(model.BaseModel):
    def to_query(self) -> Any: ...

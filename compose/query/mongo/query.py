import abc
from typing import Any

from pydantic import Field

from .. import base


class MongoQuery(base.Query, abc.ABC):
    @abc.abstractmethod
    def to_query(self) -> list[dict[str, Any]]:
        raise NotImplementedError


class MongoFilterQuery(MongoQuery):
    page: int | None = Field(None, ge=1)
    per_page: int | None = Field(None, ge=1)

    @abc.abstractmethod
    def to_query(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @property
    def can_paginate(self) -> bool:
        return self.page is not None and self.per_page is not None

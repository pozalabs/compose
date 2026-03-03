import math
from typing import Any, Self

from pydantic import Field

from . import model


class OffsetPaginationResult(model.BaseModel):
    items: list[Any]
    total: int
    page: int = Field(ge=1)
    per_page: int = Field(ge=1)
    extra: dict[str, Any] = Field(default_factory=dict)

    @property
    def prev_page(self) -> int | None:
        return self.page - 1 if self.has_prev else None

    @property
    def next_page(self) -> int | None:
        return self.page + 1 if self.has_next else None

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def pages(self) -> int:
        return math.ceil(self.total / self.per_page)

    @classmethod
    def empty(cls, page: int, per_page: int) -> Self:
        return cls(total=0, items=[], page=page, per_page=per_page)

    @property
    def is_empty(self) -> bool:
        return not self.total


class CursorPaginationResult(model.BaseModel):
    items: list[Any]
    next_cursor: str | None = None

    @classmethod
    def empty(cls) -> Self:
        return cls(items=[])

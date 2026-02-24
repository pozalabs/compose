import math
from typing import Any, Self

from pydantic import Field

from . import container


class OffsetPaginationResult(container.BaseModel):
    items: list[Any]
    total: int
    page: int | None = Field(None, ge=1)
    per_page: int | None = Field(None, ge=1)
    extra: dict[str, Any] = Field(default_factory=dict)

    @property
    def prev_page(self) -> int | None:
        return self.page - 1 if self.has_prev else None  # type: ignore

    @property
    def next_page(self) -> int | None:
        return self.page + 1 if self.has_next else None  # type: ignore

    @property
    def has_prev(self) -> bool:
        return self.page is not None and self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page is not None and self.page < self.pages

    @property
    def pages(self) -> int:
        return math.ceil(self.total / self.per_page) if self.per_page is not None else 1

    @classmethod
    def empty(cls, page: int | None = None, per_page: int | None = None) -> Self:
        return cls(total=0, items=[], page=page, per_page=per_page)

    @property
    def is_empty(self) -> bool:
        return not self.total


class CursorPaginationResult(container.BaseModel):
    items: list[Any]
    next_cursor: str | None = None
    has_next: bool = False

    @classmethod
    def empty(cls) -> Self:
        return cls(items=[])

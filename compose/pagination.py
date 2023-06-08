import math
from typing import Any, Optional

from pydantic import Field

from . import container


class Pagination(container.BaseModel):
    items: list[Any]
    total: int
    page: Optional[int] = Field(None, ge=1)
    per_page: Optional[int] = Field(None, ge=1)
    extra: dict[str, Any] = Field(default_factory=dict)

    @property
    def prev_page(self) -> Optional[int]:
        return self.page - 1 if self.has_prev else None  # type: ignore

    @property
    def next_page(self) -> Optional[int]:
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

    @property
    def is_empty(self) -> bool:
        return not self.total

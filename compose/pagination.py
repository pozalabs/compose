import math
from typing import Any, Optional

from . import container


class Pagination(container.BaseModel):
    total: int
    items: list[Any]
    page: Optional[int] = None
    per_page: Optional[int] = None
    extra: Optional[dict[str, Any]] = None

    @property
    def pages(self) -> int:
        return math.ceil(self.total / self.per_page) if self.per_page is not None else 1

    @property
    def prev_page(self) -> Optional[int]:
        return self.page - 1 if self.has_prev else None

    @property
    def has_prev(self) -> bool:
        return self.page is not None and self.page > 1

    @property
    def next_page(self) -> Optional[int]:
        return self.page + 1 if self.has_next else None

    @property
    def has_next(self) -> bool:
        return self.page is not None and self.page < self.pages

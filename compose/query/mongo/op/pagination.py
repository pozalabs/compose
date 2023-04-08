from typing import Optional

from .base import Operator
from .stage import Limit, Skip
from .types import DictExpression, ListExpression


class Pagination(Operator):
    def __init__(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        metadata_ops: Optional[list[Operator]] = None,
    ):
        if not ((page is not None and per_page is not None) or (page is None and per_page is None)):
            raise ValueError("`page` and `per_page` are mutual inclusive")

        self.page = page
        self.per_page = per_page
        self.metadata_ops = metadata_ops or []

        self.can_paginate = self.page is not None and self.per_page is not None

    def expression(self) -> DictExpression:
        return {
            "$facet": {
                "metadata": [{"$count": "total"}, *[op.expression() for op in self.metadata_ops]],
                "items": self._pagination_expression(),
            }
        }

    def _pagination_expression(self) -> ListExpression:
        if not self.can_paginate:
            return []

        return [
            Skip((self.page - 1) * self.per_page).expression(),  # type: ignore
            Limit(self.per_page).expression(),  # type: ignore
        ]

from typing import Optional

from .base import Operator
from .types import DictExpression


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
        pagination_stages = [
            {"$skip": (self.page - 1) * self.per_page},
            {"$limit": self.per_page},
        ]
        return {
            "$facet": {
                "metadata": [{"$count": "total"}, *[op.expression() for op in self.metadata_ops]],
                "items": pagination_stages if self.can_paginate else [],
            }
        }

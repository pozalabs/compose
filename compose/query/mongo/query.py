import abc
from typing import Any

from ...pagination import CursorPaginationResult, OffsetPaginationResult
from ..base import OffsetPaginationQuery, Query


class MongoQuery(Query, abc.ABC):
    @abc.abstractmethod
    def to_query(self) -> list[dict[str, Any]]:
        raise NotImplementedError


class MongoPaginationQuery[R](MongoQuery):
    @abc.abstractmethod
    def to_query(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abc.abstractmethod
    def to_result(self, raw: dict[str, Any] | None) -> R:
        raise NotImplementedError


class MongoOffsetPaginationQuery(
    OffsetPaginationQuery, MongoPaginationQuery[OffsetPaginationResult]
):
    @abc.abstractmethod
    def to_query(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def to_result(self, raw: dict[str, Any] | None) -> OffsetPaginationResult:
        if raw is None:
            return OffsetPaginationResult.empty(page=self.page, per_page=self.per_page)

        return OffsetPaginationResult(
            total=(raw["metadata"][0]["total"] if raw["metadata"] else 0),
            items=raw["items"],
            page=self.page,
            per_page=self.per_page,
        )


class MongoCursorPaginationQuery(MongoPaginationQuery[CursorPaginationResult], abc.ABC):
    per_page: int | None = None

    @abc.abstractmethod
    def derive_cursor(self, last_item: dict[str, Any]) -> str:
        raise NotImplementedError

    def to_result(self, raw: dict[str, Any] | None) -> CursorPaginationResult:
        if raw is None:
            return CursorPaginationResult.empty()

        items: list[Any] = raw["items"]

        has_next = self.per_page is not None and len(items) > self.per_page
        if has_next:
            items = items[: self.per_page]

        next_cursor = self.derive_cursor(items[-1]) if items else None

        return CursorPaginationResult(
            items=items,
            next_cursor=next_cursor,
            has_next=has_next,
        )

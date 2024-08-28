from __future__ import annotations

import abc
from typing import Any, Generic, Self, TypeVar, get_args, get_origin

from ..base import OffsetPaginationQuery, Query

T = TypeVar("T")


class Find(Generic[T]):
    def __init__(self):
        self._kwargs = {}

    def filter(self, filter_: dict[str, Any], /) -> Self:
        self._kwargs["filter"] = filter_
        return self

    def projection(self, projection: dict[str, Any], /) -> Find[dict[str, Any]]:
        self._kwargs["projection"] = projection
        return self

    def sort(self, sort: list[tuple[str, int]], /) -> Self:
        self._kwargs["sort"] = sort
        return self

    def to_query(self) -> dict[str, Any]:
        return self._kwargs

    @property
    def return_type(self) -> type[T] | type[dict[str, Any]]:
        if self._kwargs.get("projection") is not None:
            return dict[str, Any]

        # 상속하지 않고 사용하는 경우
        if (orig_class := getattr(self, "__orig_class__", None)) is not None:
            return get_args(orig_class)[0]

        orig_base = next(
            (base for base in self.__class__.__orig_bases__ if get_origin(base) is Find),
            None,
        )
        if orig_base is None:
            raise ValueError("No origin base found")

        return get_args(orig_base)[0]


class MongoQuery(Query, abc.ABC):
    @abc.abstractmethod
    def to_query(self) -> list[dict[str, Any]]:
        raise NotImplementedError


class MongoFilterQuery(OffsetPaginationQuery, MongoQuery):
    @abc.abstractmethod
    def to_query(self) -> list[dict[str, Any]]:
        raise NotImplementedError


MongoOffsetFilterQuery = MongoFilterQuery

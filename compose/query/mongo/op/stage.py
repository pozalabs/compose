from __future__ import annotations

from typing import Any, Optional, Union

from .base import Merge, Operator, Stage
from .logical import And, LogicalOperator, Or
from .pipeline import Pipeline
from .types import DictExpression, ListExpression, MongoKeyword


class Match(Stage):
    def __init__(self, op: LogicalOperator):
        self.op = op

    def expression(self) -> DictExpression:
        if not (expression := self.op.expression()):
            return {}
        return {"$match": expression}

    @classmethod
    def and_(cls, *ops: Operator) -> Match:
        return cls(And(*ops))

    @classmethod
    def or_(cls, *ops: Operator) -> Match:
        return cls(Or(*ops))


class Sort(Stage):
    def __init__(self, *ops: Operator):
        self.ops = list(ops)

    def expression(self) -> DictExpression:
        if not (merged := Merge.dict(*self.ops).expression()):
            raise ValueError("Expression cannot be empty")
        return {"$sort": merged}


class Specification(Operator):
    def __init__(self, field: str, spec: Any):
        self.field = field
        self.spec = spec

    def expression(self) -> DictExpression:
        return {self.field: self.spec}


Spec = Specification


class Project(Stage):
    def __init__(self, *specs: Specification):
        self.specs = list(specs)

    def expression(self) -> DictExpression:
        return {"$project": Merge.dict(*self.specs).expression()}


class Lookup(Stage):
    def __init__(self, from_: str, as_: str):
        self.from_ = from_
        self.as_ = as_

    def expression(self) -> DictExpression:
        return {
            "$lookup": {
                MongoKeyword.from_py(field): (
                    value.expression() if isinstance(value, Operator) else value
                )
                for field, value in self.__dict__.items()
            }
        }


class MatchLookup(Lookup):
    def __init__(self, from_: str, as_: str, local_field: str, foreign_field: str):
        super().__init__(from_=from_, as_=as_)
        self.local_field = local_field
        self.foreign_field = foreign_field


class SubqueryLookup(Lookup):
    def __init__(
        self,
        from_: str,
        as_: str,
        let: Operator,
        pipeline: Pipeline,
    ):
        super().__init__(from_=from_, as_=as_)
        self.let = let
        self.pipeline = pipeline


class Unwind(Stage):
    def __init__(
        self,
        path: str,
        include_array_index: Optional[str] = None,
        preserve_null_and_empty_arrays: Optional[bool] = None,
    ):
        self.path = path
        self.include_array_index = include_array_index
        self.preserve_null_and_empty_arrays = preserve_null_and_empty_arrays

    def expression(self) -> DictExpression:
        return {
            "$unwind": {
                MongoKeyword.from_py(field): value
                for field, value in self.__dict__.items()
                if value is not None
            }
        }


class Set(Stage):
    def __init__(self, *specs: Specification):
        self.specs = list(specs)

    def expression(self) -> DictExpression:
        return {"$set": Merge.dict(*self.specs).expression()}


class FacetSubPipeline(Operator):
    def __init__(self, output_field: str, pipeline: Pipeline):
        self.output_field = output_field
        self.pipeline = pipeline

    def expression(self) -> DictExpression:
        return {self.output_field: self.pipeline.expression()}


class Facet(Stage):
    def __init__(self, *pipelines: FacetSubPipeline):
        self.pipelines = list(pipelines)

    def expression(self) -> DictExpression:
        return {"$facet": Merge.dict(*self.pipelines).expression()}


class Skip(Stage):
    def __init__(self, skip: int):
        self.skip = skip

    def expression(self) -> DictExpression:
        return {"$skip": self.skip}


class Limit(Stage):
    def __init__(self, limit: int):
        self.limit = limit

    def expression(self) -> DictExpression:
        return {"$limit": self.limit}


class TextSearchOperator(Operator):
    def __init__(self, query: str, path: Union[str, list[str]]):
        self.query = query
        self.path = path

    def expression(self) -> DictExpression:
        return {"text": {"query": self.query, "path": self.path}}


class Search(Stage):
    def __init__(self, index: str, op: Operator):
        self.index = index
        self.op = op

    def expression(self) -> DictExpression:
        return {"$search": {"index": self.index} | self.op.expression()}


class Pagination(Stage):
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

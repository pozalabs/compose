from __future__ import annotations

from typing import Any, Optional, Union, cast

from . import Raw
from .base import EmptyStage, Evaluable, Merge, Operator, Stage
from .logical import And, LogicalOperator, Or
from .pipeline import Pipeline
from .types import DictExpression, MongoKeyword, UnwindPath


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


class Spec(Operator):
    def __init__(self, field: str, spec: Any):
        self.field = field
        self.spec = spec

    def expression(self) -> DictExpression:
        return {self.field: Evaluable(self.spec).expression()}

    @classmethod
    def include(cls, field: str) -> Spec:
        return cls(field=field, spec=1)

    @classmethod
    def exclude(cls, field: str) -> Spec:
        return cls(field=field, spec=0)


Specification = Spec


class Project(Stage):
    def __init__(self, *specs: Spec):
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
                MongoKeyword.from_py(field): Evaluable(value).expression()
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
        self.path = UnwindPath(path)
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

    @classmethod
    def preserve_missing(cls, path: str, include_array_index: Optional[str] = None) -> Unwind:
        return cls(
            path=path,
            include_array_index=include_array_index,
            preserve_null_and_empty_arrays=True,
        )


class Set(Stage):
    def __init__(self, *specs: Spec):
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
        metadata_ops: Optional[list[Stage]] = None,
        optimize_count: bool = False,
    ):
        if not ((page is not None and per_page is not None) or (page is None and per_page is None)):
            raise ValueError("`page` and `per_page` are mutual inclusive")

        self.page = page
        self.per_page = per_page
        self.metadata_ops = metadata_ops or []
        self.optimize_count = optimize_count

        self.can_paginate = self.page is not None and self.per_page is not None

    def expression(self) -> DictExpression:
        return Facet(
            FacetSubPipeline(output_field="metadata", pipeline=self._count_pipeline()),
            FacetSubPipeline(
                output_field="items",
                pipeline=self._pagination_pipeline(),
            ),
        ).expression()

    def _count_pipeline(self) -> Pipeline:
        if not self.optimize_count:
            return Pipeline(
                cast(Stage, Raw({"$count": "total"})),
                *self.metadata_ops,
            )

        return Pipeline(
            Project(Spec.include("_id")),
            Group(Raw({"total": {"$sum": 1}}), key=1),
            Project(Spec.exclude("_id")),
            *self.metadata_ops,
        )

    def _pagination_pipeline(self) -> Pipeline:
        if not self.can_paginate:
            return Pipeline(EmptyStage())

        return Pipeline(
            Skip((self.page - 1) * self.per_page),  # type: ignore
            Limit(self.per_page),  # type: ignore
        )


class ReplaceRoot(Stage):
    def __init__(self, new_root: Any):
        self.new_root = new_root

    def expression(self) -> DictExpression:
        return {"$replaceRoot": {"newRoot": Evaluable(self.new_root).expression()}}


class Group(Stage):
    def __init__(self, *ops: Operator, key: Optional[Any]):
        self.ops = list(ops)
        self.key = key

    def expression(self) -> DictExpression:
        return {
            "$group": {
                "_id": Evaluable(self.key).expression(),
                **Merge.dict(*self.ops).expression(),
            }
        }

    @classmethod
    def by_null(cls, *ops: Operator) -> Group:
        return cls(*ops, key=None)

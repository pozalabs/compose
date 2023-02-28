from __future__ import annotations

import abc
from typing import Any, Optional

from .base import Merge, Operator
from .logical import And, LogicalOperator, Or
from .types import DictExpression, ListExpression, MongoKeyword


class Stage(Operator):
    @abc.abstractmethod
    def expression(self) -> DictExpression:
        raise NotImplementedError


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
                MongoKeyword.from_py(field): value for field, value in self.__dict__.items()
            }
        }


class MatchLookup(Lookup):
    def __init__(self, from_: str, as_: str, local_field: str, foreign_field: str):
        super().__init__(from_=from_, as_=as_)
        self.local_field = local_field
        self.foreign_field = foreign_field


class SubQueryLookup(Lookup):
    def __init__(self, from_: str, as_: str, let: str, pipeline: ListExpression):
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
                MongoKeyword.from_py(field): value for field, value in self.__dict__.items()
            }
        }


class Set(Stage):
    def __init__(self, *specs: Specification):
        self.specs = list(specs)

    def expression(self) -> DictExpression:
        return {"$set": Merge.dict(*self.specs).expression()}

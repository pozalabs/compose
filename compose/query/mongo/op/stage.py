from __future__ import annotations

import abc
import functools
import operator
from typing import Any, ClassVar, Union

from .base import Operator
from .comparison import ComparisonOperator
from .logical import And, LogicalOperator, Or
from .types import DictExpression, ListExpression


class Stage(Operator):
    @abc.abstractmethod
    def expression(self) -> DictExpression:
        raise NotImplementedError


class Match(Stage):
    def __init__(self, op: LogicalOperator):
        self.op = op

    def expression(self) -> DictExpression:
        return (expression := self.op.expression()) and {"$match": expression}

    @classmethod
    def and_(cls, *ops: ComparisonOperator) -> Match:
        return cls(And(*ops))

    @classmethod
    def or_(cls, *ops: ComparisonOperator) -> Match:
        return cls(Or(*ops))


class Sort(Stage):
    def __init__(self, *ops: Operator):
        self.ops = list(ops)

    def expression(self) -> DictExpression:
        merged = functools.reduce(operator.or_, [op.expression() for op in self.ops])
        if not merged:
            raise ValueError("Expression cannot be empty")
        return {"$sort": merged}


class Specification(Operator):
    def __init__(self, field: str, spec: Union[int, bool, str, dict[str, Any]] = 1):
        self.field = field
        self.spec = spec

    def expression(self) -> DictExpression:
        return {self.field: self.spec}


class Project(Stage):
    def __init__(self, *specs: Specification):
        self.specs = list(specs)

    def expression(self) -> DictExpression:
        merged = functools.reduce(operator.or_, [spec.expression() for spec in self.specs])
        return {"$project": merged}


class BaseLookup(Stage):
    alias: ClassVar[dict[str, str]] = {
        "from_": "from",
        "as_": "as",
        "foreign_field": "foreignField",
        "local_field": "localField",
    }

    def __init__(self, from_: str, as_: str):
        self.from_ = from_
        self.as_ = as_

    def expression(self) -> DictExpression:
        return {
            "$lookup": {
                self.alias.get(field, field): value for field, value in self.__dict__.items()
            }
        }


class MatchLookup(BaseLookup):
    def __init__(self, from_: str, as_: str, local_field: str, foreign_field: str):
        super().__init__(from_=from_, as_=as_)
        self.local_field = local_field
        self.foreign_field = foreign_field


class SubQueryLookup(BaseLookup):
    def __init__(self, from_: str, as_: str, let: str, pipeline: ListExpression):
        super().__init__(from_=from_, as_=as_)
        self.let = let
        self.pipeline = pipeline

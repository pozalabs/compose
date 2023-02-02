from __future__ import annotations

import abc
import functools
import operator

from .base import Operator
from .comparison import ComparisonOperator
from .logical import And, LogicalOperator, Or
from .types import DictExpression


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

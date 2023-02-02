from __future__ import annotations

import abc

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

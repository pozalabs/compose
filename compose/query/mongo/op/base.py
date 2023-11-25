from __future__ import annotations

import abc
import functools
import operator
from collections.abc import Callable
from typing import Any, ClassVar, Optional

from .types import DictExpression, ListExpression


class Operator:
    @abc.abstractmethod
    def expression(self) -> Any:
        raise NotImplementedError


class ComparisonOperator(Operator):
    def __init__(self, field: str, value: Optional[Any] = None):
        self.field = field
        self.value = value

    @abc.abstractmethod
    def expression(self) -> dict[str, Any]:
        raise NotImplementedError


class LogicalOperator(Operator):
    def __init__(self, *ops: Operator):
        self.ops = list(ops)

    @abc.abstractmethod
    def expression(self) -> dict[str, ListExpression]:
        raise NotImplementedError


class GeneralAggregationOperator(Operator):
    mongo_operator: ClassVar[str] = ""

    def __init__(self, *expressions: Any):
        self.expressions = list(expressions)

    def expression(self) -> DictExpression:
        return {self.mongo_operator: [Evaluable(expr).expression() for expr in self.expressions]}


class Stage(Operator):
    @abc.abstractmethod
    def expression(self) -> DictExpression:
        raise NotImplementedError


class Merge(Operator):
    def __init__(self, *ops: Operator, initial: Any):
        self.ops = list(ops)
        self.initial = initial

    def expression(self) -> Any:
        return functools.reduce(operator.or_, [op.expression() for op in self.ops], self.initial)

    @classmethod
    def dict(cls, *ops: Operator) -> Merge:
        return cls(*ops, initial={})


class OpFilter(Operator):
    def __init__(self, *ops: Operator, predicate: Callable[[Operator], bool]):
        self.ops = list(ops)
        self.predicate = predicate

    def expression(self) -> ListExpression:
        return [op.expression() for op in self.ops if self.predicate(op)]

    @classmethod
    def non_empty(cls, *ops: Operator) -> OpFilter:
        return cls(*ops, predicate=lambda op: op.expression())


class Evaluable(Operator):
    def __init__(self, op: Any):
        self.op = op

    def expression(self) -> Any:
        return self.op.expression() if isinstance(self.op, Operator) else self.op

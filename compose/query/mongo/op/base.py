from __future__ import annotations

import abc
import functools
import operator
from collections.abc import Callable
from typing import Any, ClassVar, Self

from .types import DictExpression, ListExpression


class Operator(abc.ABC):
    @abc.abstractmethod
    def expression(self) -> Any:
        raise NotImplementedError

    def then(self, op: Callable[..., Operator]) -> Operator:
        return op(self.expression())


class ComparisonOperator(Operator):
    def __init__(self, field: str, value: Any | None = None):
        self.field = field
        self.value = value

    @abc.abstractmethod
    def expression(self) -> dict[str, Any]:
        raise NotImplementedError


class EqualityOperator(ComparisonOperator):
    @abc.abstractmethod
    def expression(self) -> dict[str, Any]:
        raise NotImplementedError

    @classmethod
    def is_null(cls, field: str) -> Self:
        return cls(field=field, value=None)

    @classmethod
    def is_true(cls, field: str) -> Self:
        return cls(field=field, value=True)

    @classmethod
    def is_false(cls, field: str) -> Self:
        return cls(field=field, value=False)


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
        return deep_evaluate({self.mongo_operator: self.expressions})


class Stage[T](Operator):
    @abc.abstractmethod
    def expression(self) -> T:
        raise NotImplementedError


class Merge[T](Operator):
    def __init__(self, *ops: Operator, initial: Any):
        self.ops = list(ops)
        self.initial = initial

    def expression(self) -> T:
        return functools.reduce(operator.or_, [op.expression() for op in self.ops], self.initial)

    @classmethod
    def dict(cls, *ops: *tuple[Operator, ...]) -> Merge[dict[str, Any]]:
        return cls(*ops, initial={})


def evaluate(value: Any) -> Any:
    if isinstance(value, Operator):
        return value.expression()
    return value


def deep_evaluate(value: Any) -> Any:
    match value:
        case Operator():
            return value.expression()
        case dict():
            return {k: deep_evaluate(v) for k, v in value.items()}
        case list():
            return [deep_evaluate(v) for v in value]
        case _:
            return value

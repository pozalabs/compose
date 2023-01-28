from __future__ import annotations

import abc
import functools
import operator
from collections.abc import Callable
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Expression:
    @abc.abstractmethod
    def expression(self) -> Any:
        raise NotImplementedError

    def __and__(self, other: Expression) -> Expression:
        return self and other

    def __or__(self, other: Expression) -> Expression:
        return self or other


class Empty(Expression, Generic[T]):
    def __init__(self, expression_factory: Callable[[], T]):
        self.expression_factory = expression_factory

    def expression(self) -> T:
        result = self.expression_factory()
        if result is None:
            raise ValueError("None is not allowed")
        if result:
            raise ValueError("expression is not empty")
        return result

    @classmethod
    def dict(cls) -> Empty[dict[str, Any]]:
        return cls(dict)

    def __and__(self, other: Expression) -> Expression:
        return self

    def __or__(self, other: Expression) -> Expression:
        return other


class Composed(Expression):
    def __init__(
        self,
        *expressions: Expression,
        composer: Callable[[Expression, Expression], Expression],
    ):
        self.composer = composer
        self.expressions = list(expressions)

    def expression(self) -> Any:
        first, *rest = self.expressions
        return functools.reduce(self.composer, rest, first).expression()

    @classmethod
    def and_(cls, *expressions: Expression) -> Composed:
        return cls(*expressions, composer=operator.and_)

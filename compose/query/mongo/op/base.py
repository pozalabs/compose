from __future__ import annotations

import abc
import functools
import operator
from collections.abc import Callable
from typing import Any


class Operator:
    @abc.abstractmethod
    def expression(self) -> Any:
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


class Filter(Operator):
    def __init__(self, *ops: Operator, predicate: Callable[[Operator], bool]):
        self.ops = list(ops)
        self.predicate = predicate

    def expression(self) -> list[Any]:
        return [op.expression() for op in self.ops if self.predicate(op)]

    @classmethod
    def non_empty(cls, *ops: Operator) -> Filter:
        return cls(*ops, predicate=lambda op: op.expression())

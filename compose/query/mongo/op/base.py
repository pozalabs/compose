from __future__ import annotations

import abc
import functools
import operator
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

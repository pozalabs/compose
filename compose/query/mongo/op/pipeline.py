from typing import Self

from .base import Flatten, ListExpression, Operator, OpFilter, Stage


class Pipeline(Operator):
    def __init__(self, *ops: Stage | Self):
        self.ops = list(ops)

    def expression(self) -> ListExpression:
        return Flatten(OpFilter.non_empty(*self.ops)).expression()

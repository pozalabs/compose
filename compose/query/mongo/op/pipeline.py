from typing import Self

from .base import ListExpression, Operator, OpFilter, Stage, Unpack


class Pipeline(Operator):
    def __init__(self, *ops: Stage | Self):
        self.ops = list(ops)

    def expression(self) -> ListExpression:
        return OpFilter.non_empty(Unpack(*self.ops)).expression()

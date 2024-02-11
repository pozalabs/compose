from typing import Self

from . import func
from .base import Flatten, ListExpression, Operator, Stage


class Pipeline(Operator):
    def __init__(self, *ops: Stage | Self):
        self.ops = list(ops)

    def expression(self) -> ListExpression:
        return Flatten(*func.Filter(self.ops, func.NonEmpty())).expression()

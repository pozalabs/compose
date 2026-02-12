from typing import Any

from ..base import Operator, evaluate
from ..types import DictExpression


class SetIntersection(Operator):
    def __init__(self, *values: Any):
        self.values = list(values)

    def expression(self) -> DictExpression:
        return {"$setIntersection": [evaluate(v) for v in self.values]}

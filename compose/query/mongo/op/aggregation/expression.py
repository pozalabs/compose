from typing import Any

from ..base import Evaluable, Operator
from ..types import DictExpression, _String


class Map(Operator):
    def __init__(self, input_: Any, as_: str, in_: Any):
        self.input = input_
        self.as_ = _String(as_)
        self.in_ = in_

    def expression(self) -> DictExpression:
        return {
            "$map": {
                "input": Evaluable(self.input).expression(),
                "as": self.as_,
                "in": Evaluable(self.in_).expression(),
            }
        }

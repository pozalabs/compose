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


class Size(Operator):
    def __init__(self, expression: Any):
        self.expression = expression

    def expression(self) -> DictExpression:
        return {"$size": Evaluable(self.expression).expression()}


class Filter(Operator):
    def __init__(self, input_: Any, as_: str, cond: Any, limit: Any | None = None):
        self.input = input_
        self.as_ = _String(as_)
        self.cond = cond
        self.limit = limit

    def expression(self) -> DictExpression:
        expression = {
            "input": Evaluable(self.input).expression(),
            "as": self.as_,
            "cond": Evaluable(self.cond).expression(),
        }
        if self.limit is not None:
            expression["limit"] = Evaluable(self.limit).expression()

        return {"$filter": expression}

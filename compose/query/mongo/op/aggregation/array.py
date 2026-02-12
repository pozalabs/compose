from typing import Any

from .. import utils
from ..base import Operator, evaluate

AIn = utils.create_general_aggregation_operator(name="AIn", mongo_operator="$in")


class ArrayElemAt(Operator):
    def __init__(self, array: Any, index: int, /):
        self.array = array
        self.index = index

    def expression(self) -> Any:
        return {"$arrayElemAt": [evaluate(self.array), self.index]}

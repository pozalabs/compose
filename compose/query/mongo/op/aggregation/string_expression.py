from typing import Any

from ..base import Operator, evaluate
from ..types import DictExpression


class RegexMatch(Operator):
    def __init__(self, field: Any, value: Any):
        self.field = field
        self.value = value

    def expression(self) -> DictExpression:
        return {"$regexMatch": {"input": evaluate(self.field), "regex": evaluate(self.value)}}

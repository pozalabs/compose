from typing import Any

from ..base import Operator
from ..evaulation import Expr
from ..raw import Raw
from ..types import DictExpression


class RegexMatch(Operator):
    def __init__(self, field: Any, value: Any):
        self.field = field
        self.value = value

    def expression(self) -> DictExpression:
        return Expr(Raw({"$regexMatch": {"input": self.field, "regex": self.value}})).expression()

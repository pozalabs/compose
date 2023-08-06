from __future__ import annotations

from typing import Any, Optional

from ..base import Evaluable, Operator
from ..types import DictExpression


class IfNull(Operator):
    def __init__(
        self,
        input_expr: str,
        non_null_input_expr: Any,
        replacement_expr: Optional[Any] = None,
        /,
    ):
        """
        Aggregation operator `$ifNull`

        Reference:
            https://www.mongodb.com/docs/manual/reference/operator/aggregation/ifNull/#mongodb-expression-exp.-ifNull
        """

        self.input_expr = input_expr
        self.non_null_input_expr = non_null_input_expr
        self.replacement_expr = replacement_expr

    @classmethod
    def single(cls, input_expr: str, non_null_input_expr: Any, /) -> IfNull:
        return cls(input_expr, non_null_input_expr)

    @classmethod
    def multiple(
        cls, input_expr: str, non_null_input_expr: Any, replacement_expr: Any, /
    ) -> IfNull:
        return cls(input_expr, non_null_input_expr, replacement_expr)

    def expression(self) -> DictExpression:
        expressions = [self.input_expr, self.non_null_input_expr]
        if self.replacement_expr is not None:
            expressions.append(self.replacement_expr)

        return {"$ifNull": [Evaluable(expr).expression() for expr in expressions]}


class Cond(Operator):
    def __init__(self, if_: Any, then: Any, else_: Any):
        """
        Aggregation operator `$cond`

        Reference:
            https://www.mongodb.com/docs/manual/reference/operator/aggregation/cond/#mongodb-expression-exp.-cond
        """

        self.if_ = if_
        self.then = then
        self.else_ = else_

    def expression(self) -> DictExpression:
        return {
            "$cond": {
                "if": Evaluable(self.if_).expression(),
                "then": Evaluable(self.then).expression(),
                "else": Evaluable(self.else_).expression(),
            }
        }

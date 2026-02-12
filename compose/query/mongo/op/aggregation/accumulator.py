from typing import Any

from ..base import DictExpression, Operator, evaluate


class First(Operator):
    def __init__(self, expression: Any, /):
        self._expression = expression

    def expression(self) -> DictExpression:
        return {"$first": evaluate(self._expression)}


class MergeObjects(Operator):
    def __init__(self, *expressions: Any):
        self._expressions = list(expressions)

    def expression(self) -> DictExpression:
        expressions = [evaluate(e) for e in self._expressions]
        return {"$mergeObjects": expressions if len(expressions) > 1 else expressions[0]}


class AddToSet(Operator):
    def __init__(self, expression: Any, /):
        self._expression = expression

    def expression(self) -> DictExpression:
        return {"$addToSet": evaluate(self._expression)}


class Push(Operator):
    def __init__(self, expression: Any, /):
        self._expression = expression

    def expression(self) -> DictExpression:
        return {"$push": evaluate(self._expression)}

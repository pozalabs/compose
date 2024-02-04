from typing import Any, Self

from ..base import Evaluable, Operator
from ..types import DictExpression, MongoKeyword, _String


class Map(Operator):
    def __init__(self, input_: Any, as_: str, in_: Any):
        self.input = input_
        self.as_ = _String(as_)
        self.in_ = in_

    def expression(self) -> DictExpression:
        return {
            "$map": {
                MongoKeyword.from_py(field): Evaluable(value).expression()
                for field, value in self.__dict__.items()
            }
        }


class Size(Operator):
    def __init__(self, expression: Any):
        self._expression = expression

    def expression(self) -> DictExpression:
        return {"$size": Evaluable(self._expression).expression()}


class Filter(Operator):
    def __init__(self, input_: Any, as_: str, cond: Any, limit: Any | None = None):
        self.input = input_
        self.as_ = _String(as_)
        self.cond = cond
        self.limit = limit

    def expression(self) -> DictExpression:
        return {
            "$filter": {
                MongoKeyword.from_py(field): Evaluable(value).expression()
                for field, value in self.__dict__.items()
                if value is not None
            },
        }


class Reduce(Operator):
    def __init__(self, input_: Any, initial_value: Any, in_: Any):
        self.input = input_
        self.initial_value = initial_value
        self.in_ = in_

    def expression(self) -> DictExpression:
        return {
            "$reduce": {
                MongoKeyword.from_py(field): Evaluable(value).expression()
                for field, value in self.__dict__.items()
            }
        }

    @classmethod
    def list(cls, input_: Any, in_: Any) -> Self:
        return cls(input_=input_, initial_value=[], in_=in_)

    @classmethod
    def int(cls, input_: Any, in_: Any) -> Self:
        return cls(input_=input_, initial_value=0, in_=in_)

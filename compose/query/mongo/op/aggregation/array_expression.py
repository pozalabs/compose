from typing import Any, Self, Unpack

from ..base import Merge, Operator, deep_evaluate, evaluate
from ..sort import SortBy
from ..types import DictExpression, _String


class Map(Operator):
    def __init__(self, input_: Any, as_: str, in_: Any):
        self.input = input_
        self.as_ = _String(as_)
        self.in_ = in_

    def expression(self) -> DictExpression:
        return {
            "$map": {
                "input": evaluate(self.input),
                "as": self.as_,
                "in": deep_evaluate(self.in_),
            }
        }


class Size(Operator):
    def __init__(self, expression: Any):
        self._expression = expression

    def expression(self) -> DictExpression:
        return {"$size": deep_evaluate(self._expression)}


class Filter(Operator):
    def __init__(self, input_: Any, as_: str, cond: Any, limit: Any | None = None):
        self.input = input_
        self.as_ = _String(as_)
        self.cond = cond
        self.limit = limit

    def expression(self) -> DictExpression:
        result: DictExpression = {
            "input": evaluate(self.input),
            "as": self.as_,
            "cond": deep_evaluate(self.cond),
        }
        if self.limit is not None:
            result["limit"] = evaluate(self.limit)
        return {"$filter": result}


class Reduce(Operator):
    def __init__(self, input_: Any, initial_value: Any, in_: Any):
        self.input = input_
        self.initial_value = initial_value
        self.in_ = in_

    def expression(self) -> DictExpression:
        return {
            "$reduce": {
                "input": evaluate(self.input),
                "initialValue": evaluate(self.initial_value),
                "in": deep_evaluate(self.in_),
            }
        }

    @classmethod
    def into_list(cls, input_: Any, in_: Any) -> Self:
        return cls(input_=input_, initial_value=[], in_=in_)

    @classmethod
    def into_int(cls, input_: Any, in_: Any) -> Self:
        return cls(input_=input_, initial_value=0, in_=in_)


class SortArray(Operator):
    def __init__(self, input_: Any, *sort_by: Unpack[tuple[SortBy, ...]]):
        self.input = input_
        self.sort_by = sort_by

    def expression(self) -> DictExpression:
        return {
            "$sortArray": {
                "input": deep_evaluate(self.input),
                "sortBy": Merge.dict(*self.sort_by).expression(),
            }
        }


class IndexOfArray(Operator):
    def __init__(
        self,
        array: Any,
        search: Any,
        /,
        *,
        start: Any | None = None,
        end: Any | None = None,
    ):
        self.array = array
        self.search = search
        self.start = start
        self.end = end

        if self.end is not None and self.start is None:
            raise ValueError("`end` must be used with `start`")

    def expression(self) -> DictExpression:
        args = [self.array, self.search]
        for v in (self.start, self.end):
            if v is not None:
                args.append(v)

        return {"$indexOfArray": [evaluate(a) for a in args]}

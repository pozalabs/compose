from typing import Any

import pytest

from compose.query.mongo import op
from compose.query.mongo.op import ComparisonOperator, EmptyOnNull


class CustomOp(ComparisonOperator):
    def __init__(self, field: str, value: Any | None = None):
        super().__init__(field=field, value=value)

    def expression(self) -> dict[str, Any]:
        return {self.field: self.value}


@pytest.mark.parametrize(
    "op, expected",
    [
        (CustomOp(field="field", value=None), {}),
        (CustomOp(field="field", value="value"), {"field": "value"}),
    ],
    ids=(
        "비교 대상이 None인 표현식을 감싸면 빈 표현식 리턴",
        "비교 대상이 None이 아닌 표현식을 감싸면 원래 표현식 리턴",
    ),
)
def test_empty_on_null(op: ComparisonOperator, expected: dict[str, Any]):
    expression = EmptyOnNull(op).expression()

    assert expression == expected


@pytest.mark.parametrize(
    "op, expected",
    [
        (op.Eq.from_(name="test"), {"name": {"$eq": "test"}}),
        (op.Ne.from_(age=30), {"age": {"$ne": 30}}),
    ],
)
def test_instantiate_using_from_(operator: ComparisonOperator, expected: dict[str, Any]):
    assert operator.expression() == expected

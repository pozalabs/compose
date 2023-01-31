from typing import Any, Optional

import pytest

from compose.query.mongo.op import ComparisonOperator, EmptyOnNull


class TestOp(ComparisonOperator):
    def __init__(self, field: str, value: Optional[Any] = None):
        super().__init__(field=field, value=value)

    def expression(self) -> dict[str, Any]:
        return {self.field: self.value}


@pytest.mark.parametrize(
    "op, expected",
    [
        (TestOp(field="field", value=None), {}),
        (TestOp(field="field", value="value"), {"field": "value"}),
    ],
    ids=(
        "비교 대상이 None인 표현식을 감싸면 빈 표현식 리턴",
        "비교 대상이 None이 아닌 표현식을 감싸면 원래 표현식 리턴",
    ),
)
def test_empty_on_null(op: ComparisonOperator, expected: dict[str, Any]):
    expression = EmptyOnNull(op).expression()

    assert expression == expected

from typing import Any

import pytest

from compose.query.mongo.op import Evaluable, Spec


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            Evaluable(Spec(field="field", spec=1)),
            {"field": 1},
        ),
        (
            Evaluable({"field": 1}),
            {"field": 1},
        ),
        (
            Evaluable("$field"),
            "$field",
        ),
    ],
    ids=(
        "`Operator`를 입력하면 평가한 표현식을 리턴한다.",
        "딕셔너리를 입력하면 값을 그대로 리턴한다",
        "문자열을 입력하면 값을 그대로 리턴한다",
    ),
)
def test_expression(op: Evaluable, expected: Any):
    assert op.expression() == expected

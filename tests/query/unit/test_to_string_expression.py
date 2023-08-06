import pytest

from compose.query.mongo.op import DictExpression, ToString


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            ToString("$field"),
            {"$toString": "$field"},
        ),
    ],
)
def test_expression(op: ToString, expected: DictExpression):
    assert op.expression() == expected

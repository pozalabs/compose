import pytest

from compose.query.mongo.op import DictExpression, ToInt


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            ToInt("$field"),
            {"$toInt": "$field"},
        ),
    ],
)
def test_expression(op: ToInt, expected: DictExpression):
    assert op.expression() == expected

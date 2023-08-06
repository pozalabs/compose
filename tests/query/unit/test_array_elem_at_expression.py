import pytest

from compose.query.mongo.op import ArrayElemAt, DictExpression


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            ArrayElemAt([1, 2, 3], 0),
            {"$arrayElemAt": [[1, 2, 3], 0]},
        ),
        (
            ArrayElemAt("$field", 0),
            {"$arrayElemAt": ["$field", 0]},
        ),
    ],
)
def test_expression(op: ArrayElemAt, expected: DictExpression):
    assert op.expression() == expected

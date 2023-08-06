import pytest

from compose.query.mongo.op import Concat, DictExpression


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            Concat("$a", "-", "$b"),
            {"$concat": ["$a", "-", "$b"]},
        ),
        (
            Concat({"$toString": "$a"}, "-", "$b"),
            {"$concat": [{"$toString": "$a"}, "-", "$b"]},
        ),
    ],
)
def test_expression(op: Concat, expected: DictExpression):
    assert op.expression() == expected

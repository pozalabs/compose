import pytest

from compose.query.mongo.op import DictExpression, Split


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            Split("$field", "-"),
            {"$split": ["$field", "-"]},
        ),
        (
            Split("string", "-"),
            {"$split": ["string", "-"]},
        ),
    ],
)
def test_expression(op: Split, expected: DictExpression):
    assert op.expression() == expected

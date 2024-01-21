import pytest

from compose.query.mongo.op import AddToSet, DictExpression


@pytest.mark.parametrize(
    "op,expected",
    [
        (AddToSet("$field1"), {"$addToSet": "$field1"}),
        (AddToSet([1, 2]), {"$addToSet": [1, 2]}),
    ],
)
def test_expression(op: AddToSet, expected: DictExpression):
    assert op.expression() == expected

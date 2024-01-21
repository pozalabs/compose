import pytest

from compose.query.mongo.op import DictExpression, SetUnion


@pytest.mark.parametrize(
    "op,expected",
    [
        (SetUnion("$field1", "$field2"), {"$setUnion": ["$field1", "$field2"]}),
        (SetUnion([1, 2], [1, 2, 3]), {"$setUnion": [[1, 2], [1, 2, 3]]}),
    ],
)
def test_expression(op: SetUnion, expected: DictExpression):
    assert op.expression() == expected

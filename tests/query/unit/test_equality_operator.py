import pytest

from compose.query.mongo.op import DictExpression, Eq, EqualityOperator, Ne


@pytest.mark.parametrize(
    "op, expected",
    [
        (Eq.is_null("field"), {"field": {"$eq": None}}),
        (Eq.is_true("field"), {"field": {"$eq": True}}),
        (Eq.is_false("field"), {"field": {"$eq": False}}),
        (Ne.is_false("field"), {"field": {"$ne": False}}),
        (Ne.is_true("field"), {"field": {"$ne": True}}),
        (Ne.is_false("field"), {"field": {"$ne": False}}),
    ],
)
def test_expression(op: EqualityOperator, expected: DictExpression):
    assert op.expression() == expected

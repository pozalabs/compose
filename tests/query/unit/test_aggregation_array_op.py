import pytest

from compose.query.mongo.op import AIn, DictExpression, Operator


@pytest.mark.parametrize(
    "op, expected",
    [(AIn, "AIn")],
)
def test_op_name(op: type[Operator], expected: str):
    assert op.__name__ == expected


@pytest.mark.parametrize(
    "op, expected",
    [
        (AIn("$field", "value"), {"$in": ["$field", "value"]}),
    ],
)
def test_expression(op: Operator, expected: DictExpression):
    assert op.expression() == expected

import pytest

from compose.query.mongo.op import AEq, AGt, AGte, ALt, ALte, ANe, DictExpression, Operator


@pytest.mark.parametrize(
    "op, expected",
    [
        (AEq, "AEq"),
        (ANe, "ANe"),
        (AGt, "AGt"),
        (AGte, "AGte"),
        (ALt, "ALt"),
        (ALte, "ALte"),
    ],
)
def test_op_name(op: type[Operator], expected: str):
    assert op.__name__ == expected


@pytest.mark.parametrize(
    "op, expected",
    [
        (AEq("$field", "value"), {"$eq": ["$field", "value"]}),
        (ANe("$field", "value"), {"$ne": ["$field", "value"]}),
        (AGt("$field", 1), {"$gt": ["$field", 1]}),
        (AGte("$field", 1), {"$gte": ["$field", 1]}),
        (ALt("$field", 1), {"$lt": ["$field", 1]}),
        (ALte("$field", 1), {"$lte": ["$field", 1]}),
    ],
)
def test_expression(op: Operator, expected: DictExpression):
    assert op.expression() == expected

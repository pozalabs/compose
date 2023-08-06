import pytest

from compose.query.mongo.op import AEq, Cond, DictExpression


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            Cond(if_=AEq("$field", "value"), then="value2", else_="value3"),
            {"$cond": {"if": {"$eq": ["$field", "value"]}, "then": "value2", "else": "value3"}},
        ),
        (
            Cond(if_={"$gte": ["$field", 100]}, then=20, else_=20),
            {"$cond": {"if": {"$gte": ["$field", 100]}, "then": 20, "else": 20}},
        ),
    ],
)
def test_expression(op: Cond, expected: DictExpression):
    assert op.expression() == expected

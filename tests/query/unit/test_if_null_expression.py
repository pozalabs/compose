import pytest

from compose.query.mongo.op import DictExpression, IfNull, Raw


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            IfNull("$field", "$expr"),
            {"$ifNull": ["$field", "$expr"]},
        ),
        (
            IfNull("$field", {"$toString": "$expr"}),
            {"$ifNull": ["$field", {"$toString": "$expr"}]},
        ),
        (
            IfNull("$field", Raw({"$toString": "$expr"})),
            {"$ifNull": ["$field", {"$toString": "$expr"}]},
        ),
        (
            IfNull("$field", "$expr", "$replacement"),
            {"$ifNull": ["$field", "$expr", "$replacement"]},
        ),
    ],
)
def test_expression(op: IfNull, expected: DictExpression):
    assert op.expression() == expected

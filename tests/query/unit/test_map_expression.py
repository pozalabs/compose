import pytest

from compose.query.mongo.op import DictExpression, Map, ToString


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            Map(input_="$field", as_="output", in_="$expr"),
            {"$map": {"input": "$field", "as": "output", "in": "$expr"}},
        ),
        (
            Map(input_="$field", as_="output", in_={"$toString": "$field"}),
            {"$map": {"input": "$field", "as": "output", "in": {"$toString": "$field"}}},
        ),
        (
            Map(input_="$field", as_="output", in_=ToString("$field")),
            {"$map": {"input": "$field", "as": "output", "in": {"$toString": "$field"}}},
        ),
    ],
)
def test_expression(op: Map, expected: DictExpression):
    assert op.expression() == expected


def test_cannot_use_path_variable_as_as_variable():
    with pytest.raises(ValueError):
        Map(input_="$field", as_="$field", in_="$expr")

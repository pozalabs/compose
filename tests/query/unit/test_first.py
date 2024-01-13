import pytest

from compose.query.mongo.op import AEq, DictExpression, Filter, First


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            First([1, 2, 3]),
            {"$first": [1, 2, 3]},
        ),
        (
            First("$field"),
            {"$first": "$field"},
        ),
        (
            First(
                Filter(
                    input_="$inputs",
                    as_="input",
                    cond=AEq("$$input.name", "name"),
                )
            ),
            {
                "$first": {
                    "$filter": {
                        "input": "$inputs",
                        "as": "input",
                        "cond": {"$eq": ["$$input.name", "name"]},
                    }
                }
            },
        ),
    ],
)
def test_expression(op: First, expected: DictExpression):
    assert op.expression() == expected

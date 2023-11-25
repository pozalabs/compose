import pytest

from compose.query.mongo.op import DictExpression, Filter


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            Filter(
                input_="$field",
                as_="output",
                cond={"$eq": ["$$field", "value"]},
            ),
            {
                "$filter": {
                    "input": "$field",
                    "as": "output",
                    "cond": {"$eq": ["$$field", "value"]},
                }
            },
        ),
        (
            Filter(
                input_="$field",
                as_="output",
                cond={"$eq": ["$$field", "value"]},
                limit=1,
            ),
            {
                "$filter": {
                    "input": "$field",
                    "as": "output",
                    "cond": {"$eq": ["$$field", "value"]},
                    "limit": 1,
                }
            },
        ),
        (
            Filter(
                input_="$field",
                as_="output",
                cond={"$eq": ["$$field", "value"]},
                limit={"$add": [0, 1]},
            ),
            {
                "$filter": {
                    "input": "$field",
                    "as": "output",
                    "cond": {"$eq": ["$$field", "value"]},
                    "limit": {"$add": [0, 1]},
                }
            },
        ),
    ],
)
def test_expression(op: Filter, expected: DictExpression):
    assert op.expression() == expected

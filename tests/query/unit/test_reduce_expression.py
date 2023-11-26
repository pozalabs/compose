import pytest

from compose.query.mongo.op import DictExpression, Reduce


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            Reduce(
                input_="$field",
                initial_value=[],
                in_={"$setUnion": ["$$value", "$$this.song_forms"]},
            ),
            {
                "$reduce": {
                    "input": "$field",
                    "initialValue": [],
                    "in": {"$setUnion": ["$$value", "$$this.song_forms"]},
                }
            },
        ),
        (
            Reduce(
                input_="$field",
                initial_value=0,
                in_={"$add": ["$$value", "$$this.total"]},
            ),
            {
                "$reduce": {
                    "input": "$field",
                    "initialValue": 0,
                    "in": {"$add": ["$$value", "$$this.total"]},
                }
            },
        ),
    ],
)
def test_expression(op: Reduce, expected: DictExpression):
    assert op.expression() == expected

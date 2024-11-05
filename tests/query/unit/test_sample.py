import pytest

from compose.query.mongo.op import DictExpression, Sample


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            Sample(3),
            {"$size": {"size": 3}},
        )
    ],
)
def test_expression(op: Sample, expected: DictExpression):
    assert op.expression() == expected

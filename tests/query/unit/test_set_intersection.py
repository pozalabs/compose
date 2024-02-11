import pytest

from compose.query.mongo.op import DictExpression, SetIntersection


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            SetIntersection([1, 2, 3], [3, 4, 5], "array", ["array"]),
            {"$setIntersection": [[1, 2, 3], [3, 4, 5], "array", ["array"]]},
        ),
    ],
)
def test_expression(op: SetIntersection, expected: DictExpression) -> None:
    assert op.expression() == expected

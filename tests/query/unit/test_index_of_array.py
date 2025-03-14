import pytest

from compose.query.mongo.op import DictExpression, IndexOfArray


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            IndexOfArray("$array", "$$id"),
            {"$indexOfArray": ["$array", "$$id"]},
        ),
        (
            IndexOfArray(
                "$array",
                "$$id",
                start=1,
            ),
            {"$indexOfArray": ["$array", "$$id", 1]},
        ),
        (
            IndexOfArray(
                "$array",
                "$$id",
                start=1,
                end=2,
            ),
            {"$indexOfArray": ["$array", "$$id", 1, 2]},
        ),
    ],
)
def test_expression(op: IndexOfArray, expected: DictExpression):
    assert op.expression() == expected


def test_cannot_use_end_without_start():
    with pytest.raises(ValueError) as exc_info:
        IndexOfArray(
            "$array",
            "$$id",
            end=2,
        )

    assert "`end` must be used with `start`" in str(exc_info.value)

import pytest

from compose.query.mongo.op import DictExpression, SortArray, SortBy


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            SortArray(
                "$field",
                SortBy.asc(field="field"),
            ),
            {
                "$sortArray": {
                    "input": "$field",
                    "sortBy": {"field": 1},
                }
            },
        ),
        (
            SortArray(
                "$field",
                SortBy.asc(field="field1"),
                SortBy.desc(field="field2"),
            ),
            {
                "$sortArray": {
                    "input": "$field",
                    "sortBy": {"field1": 1, "field2": -1},
                }
            },
        ),
    ],
)
def test_expression(op: SortArray, expected: DictExpression):
    assert op.expression() == expected

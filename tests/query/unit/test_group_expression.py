import pytest

from compose.query.mongo.op import DictExpression, Group, Spec


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            Group(
                Spec(field="field1", spec={"$sum": 1}),
                Spec(field="field2", spec={"$push": "$_id"}),
                key="$field",
            ),
            {
                "$group": {
                    "_id": "$field",
                    "field1": {"$sum": 1},
                    "field2": {"$push": "$_id"},
                }
            },
        ),
        (
            Group(
                Spec(field="field1", spec={"$sum": 1}),
                Spec(field="field2", spec={"$push": "$_id"}),
                key={"key": "$field"},
            ),
            {
                "$group": {
                    "_id": {"key": "$field"},
                    "field1": {"$sum": 1},
                    "field2": {"$push": "$_id"},
                }
            },
        ),
        (
            Group(
                Spec(field="field1", spec={"$sum": 1}),
                Spec(field="field2", spec={"$push": "$_id"}),
                key=Spec(field="key", spec="$field"),
            ),
            {
                "$group": {
                    "_id": {"key": "$field"},
                    "field1": {"$sum": 1},
                    "field2": {"$push": "$_id"},
                }
            },
        ),
        (
            Group(
                Spec(field="count", spec={"$count": {}}),
                key=None,
            ),
            {
                "$group": {
                    "_id": None,
                    "count": {"$count": {}},
                }
            },
        ),
        (
            Group.by_null(Spec(field="count", spec={"$count": {}})),
            {
                "$group": {
                    "_id": None,
                    "count": {"$count": {}},
                }
            },
        ),
    ],
    ids=(
        "문자열 리터럴을 그룹 키로 사용",
        "표현식을 그룹 키로 사용",
        "`Operator`를 그룹 키로 사용",
        "`None`을 그룹 키로 사용",
        "`by_null()` 메서드를 사용하면 `None`을 키로 사용한다.",
    ),
)
def test_expression(op: Group, expected: DictExpression):
    assert op.expression() == expected

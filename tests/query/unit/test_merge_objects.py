import pytest

from compose.query.mongo.op import DictExpression, First, MergeObjects, Spec


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            MergeObjects({"a": 1}),
            {"$mergeObjects": {"a": 1}},
        ),
        (
            MergeObjects({"a": 1}, {"b": 2}),
            {"$mergeObjects": [{"a": 1}, {"b": 2}]},
        ),
        (
            MergeObjects("$$object", Spec(field="field", spec=First("$field2"))),
            {
                "$mergeObjects": [
                    "$$object",
                    {
                        "field": {
                            "$first": "$field2",
                        }
                    },
                ]
            },
        ),
    ],
)
def test_expression(op: MergeObjects, expected: DictExpression):
    assert op.expression() == expected

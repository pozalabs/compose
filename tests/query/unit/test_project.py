import pytest

from compose.query.mongo import op
from compose.query.mongo.op import Project


@pytest.mark.parametrize(
    "project, expected",
    [
        (
            Project(
                op.Spec.include("field1"),
                op.Spec.exclude("field2"),
                op.Spec("field3", "$field3"),
                op.Spec("field4", "$ref.field4"),
            ),
            {
                "$project": {
                    "field1": 1,
                    "field2": 0,
                    "field3": "$field3",
                    "field4": "$ref.field4",
                }
            },
        ),
        (
            Project.from_attrs(
                field1=1,
                field2=0,
                field3="$field3",
                field4="$ref.field4",
            ),
            {
                "$project": {
                    "field1": 1,
                    "field2": 0,
                    "field3": "$field3",
                    "field4": "$ref.field4",
                }
            },
        ),
        (
            Project.from_(
                include=["field1"],
                exclude=["field2"],
                ref={"field3": "$field3", "field4": "$ref.field4"},
            ),
            {
                "$project": {
                    "field1": 1,
                    "field2": 0,
                    "field3": "$field3",
                    "field4": "$ref.field4",
                }
            },
        ),
    ],
    ids=[
        "spec",
        "from_attrs",
        "from_",
    ],
)
def test_expression(project: op.Project, expected: op.DictExpression):
    assert project.expression() == expected

import pytest

from compose.query.mongo.op import DictExpression, Pipeline, Project, Specification, SubqueryLookup


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            SubqueryLookup(
                from_="from_field",
                as_="as_field",
                let=Specification(field="let_field", spec="$let_field"),
                pipeline=Pipeline(Project(Specification("_id", 1))),
            ),
            {
                "$lookup": {
                    "from": "from_field",
                    "as": "as_field",
                    "let": {"let_field": "$let_field"},
                    "pipeline": [{"$project": {"_id": 1}}],
                }
            },
        ),
    ],
)
def test_expression(op: SubqueryLookup, expected: DictExpression):
    assert op.expression() == expected

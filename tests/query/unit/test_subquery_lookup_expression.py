import pytest

from compose.query.mongo.op import DictExpression, Pipeline, Project, Spec, SubqueryLookup


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            SubqueryLookup(
                from_="from_field",
                as_="as_field",
                let=Spec(field="let_field", spec="$let_field"),
                pipeline=Pipeline(Project(Spec("_id", 1))),
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
        (
            SubqueryLookup(
                from_="from_field",
                pipeline=Pipeline(Project(Spec("_id", 1))),
            ),
            {
                "$lookup": {
                    "from": "from_field",
                    "as": "from_field",
                    "pipeline": [{"$project": {"_id": 1}}],
                }
            },
        ),
    ],
    ids=[
        "let이 제공되면 출력에 포함",
        "let이 None이면 출력에서 제외",
    ],
)
def test_expression(op: SubqueryLookup, expected: DictExpression):
    assert op.expression() == expected

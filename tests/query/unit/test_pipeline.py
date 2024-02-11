import pytest

from compose.query.mongo.op import (
    Eq,
    Flatten,
    ListExpression,
    Match,
    MatchLookup,
    Pipeline,
    Set,
    Spec,
)


@pytest.mark.parametrize(
    "op,expected",
    [
        (
            Pipeline(
                Match.and_(
                    Eq(field="field", value="value"),
                ),
                Pipeline(
                    MatchLookup(
                        from_="from",
                        local_field="local_field",
                        foreign_field="foreign_field",
                        as_="as",
                    ),
                    Set(Spec(field="new_field", spec="new_value")),
                ),
            ),
            [
                {"$match": {"$and": [{"field": {"$eq": "value"}}]}},
                {
                    "$lookup": {
                        "from": "from",
                        "localField": "local_field",
                        "foreignField": "foreign_field",
                        "as": "as",
                    }
                },
                {"$set": {"new_field": "new_value"}},
            ],
        ),
    ],
)
def test_expression(op: Flatten, expected: ListExpression):
    assert op.expression() == expected

import pendulum
import pytest

from compose.query.mongo.op import (
    Eq,
    EqualityLookup,
    Limit,
    ListExpression,
    Match,
    Pipeline,
    Range,
    Set,
    SkipNull,
    Sort,
    SortBy,
    Spec,
)


@pytest.mark.parametrize(
    "op,expected",
    [
        (
            Pipeline(
                Match.and_(
                    Eq(field="field", value="value"),
                    Range.date(
                        field="created_at",
                        start=pendulum.datetime(2024, 10, 1),
                        end=pendulum.datetime(2024, 10, 2),
                    ),
                ),
                Pipeline(
                    EqualityLookup(
                        from_="from",
                        local_field="local_field",
                        foreign_field="foreign_field",
                        as_="as",
                    ),
                    Set(Spec(field="new_field", spec="new_value")),
                ),
            ),
            [
                {
                    "$match": {
                        "$and": [
                            {"field": {"$eq": "value"}},
                            {
                                "created_at": {
                                    "$gte": pendulum.datetime(2024, 10, 1),
                                    "$lt": pendulum.datetime(2024, 10, 2),
                                }
                            },
                        ]
                    }
                },
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
def test_expression(op: Pipeline, expected: ListExpression):
    assert op.expression() == expected


def test_skip_empty_stage():
    op = Pipeline(
        Match(SkipNull(Eq(field="status", value=None))),
        Sort(SortBy.asc("created_at")),
        Limit(10),
    )

    assert op.expression() == [
        {"$sort": {"created_at": 1}},
        {"$limit": 10},
    ]

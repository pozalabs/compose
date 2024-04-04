import pendulum
import pytest

from compose.query.mongo.op import (
    CursorDecoder,
    CursorEncoder,
    CursorPagination,
    ListExpression,
    Sort,
    SortBy,
)


@pytest.mark.parametrize(
    "pagination, expected",
    [
        (
            CursorPagination(
                sort=Sort(SortBy.desc(field="created_at")),
                cursor_decoder=CursorDecoder(parsers={"created_at": pendulum.parse}),
                cursor=CursorEncoder(cursor_keys=["created_at"]).encode(
                    {"created_at": pendulum.datetime(2024, 4, 1).isoformat()}
                ),
                per_page=10,
            ),
            [
                {
                    "$match": {
                        "$nor": [
                            {"created_at": {"$lt": pendulum.datetime(2024, 4, 1)}},
                        ]
                    }
                },
                {"$sort": {"created_at": -1}},
                {"$limit": 10},
                {
                    "$group": {
                        "_id": None,
                        "items": {"$push": "$$ROOT"},
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "items": 1,
                        "metadata": {"cursor_keys": ["created_at"]},
                    }
                },
            ],
        )
    ],
)
def test_expression(pagination: CursorPagination, expected: ListExpression):
    assert pagination.expression() == expected

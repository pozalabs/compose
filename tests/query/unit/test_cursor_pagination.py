import pendulum
import pytest

import compose
from compose.query.mongo.op import (
    Cursor,
    CursorPagination,
    ListExpression,
    Sort,
    SortBy,
)


class TCursor(Cursor):
    created_at: compose.types.DateTime
    id: compose.types.PyObjectId = compose.field.IdField()


@pytest.mark.parametrize(
    "pagination, expected",
    [
        (
            CursorPagination(
                sort=Sort(
                    SortBy.desc("created_at"),
                    SortBy.asc("_id"),
                ),
                cursor=TCursor(
                    created_at=pendulum.datetime(2024, 4, 1),
                    id=compose.types.PyObjectId(b"test-id-0001"),
                ),
                per_page=10,
            ),
            [
                {
                    "$match": {
                        "$or": [
                            {"$and": [{"created_at": {"$lt": pendulum.datetime(2024, 4, 1)}}]},
                            {
                                "$and": [
                                    {"created_at": {"$eq": pendulum.datetime(2024, 4, 1)}},
                                    {"_id": {"$gt": compose.types.PyObjectId(b"test-id-0001")}},
                                ]
                            },
                        ]
                    }
                },
                {"$sort": {"created_at": -1, "_id": 1}},
                {"$limit": 11},
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
                    }
                },
            ],
        )
    ],
)
def test_expression(pagination: CursorPagination, expected: ListExpression):
    assert pagination.expression() == expected

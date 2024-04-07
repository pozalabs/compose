import pendulum
import pytest

import compose
from compose.query.mongo.op import (
    Cursor,
    CursorPagination,
    CursorPaginationClause,
    DictExpression,
    ListExpression,
    Sort,
    SortBy,
)


class TCursor(Cursor):
    created_at: compose.types.DateTime
    id: compose.types.PyObjectId = compose.field.IdField()


def test_cursor_encode_decode():
    cursor = TCursor(
        created_at=pendulum.datetime(2024, 4, 1),
        id=compose.types.PyObjectId(b"test-id-0001"),
    )

    assert TCursor.from_str(cursor.to_str()) == cursor


@pytest.mark.parametrize(
    "clause, expected",
    [
        (
            CursorPaginationClause.from_cursor_params(
                sort_field="created_at",
                cursor_params=[("created_at", pendulum.datetime(2024, 4, 1))],
                sort=Sort(
                    SortBy.asc("created_at"),
                ),
            ),
            {"$and": [{"created_at": {"$gt": pendulum.datetime(2024, 4, 1)}}]},
        ),
        (
            CursorPaginationClause.from_cursor_params(
                sort_field="_id",
                cursor_params=[
                    ("created_at", pendulum.datetime(2024, 4, 1)),
                    ("_id", compose.types.PyObjectId(b"test-id-0001")),
                ],
                sort=Sort(
                    SortBy.asc("created_at"),
                    SortBy.desc("_id"),
                ),
            ),
            {
                "$and": [
                    {"created_at": {"$eq": pendulum.datetime(2024, 4, 1)}},
                    {"_id": {"$lt": compose.types.PyObjectId(b"test-id-0001")}},
                ]
            },
        ),
    ],
    ids=(
        "`sort_field`와 현재 커서 파라미터가 일치하면 정렬 방향에 따른 비교 연산자를 사용한다.",
        "`sort_field`와 일치하지 않는 커서 파라미터에는 동등 연산자를 사용한다.",
    ),
)
def test_cursor_pagination_clause_expression(
    clause: CursorPaginationClause,
    expected: DictExpression,
):
    assert clause.expression() == expected


@pytest.mark.parametrize(
    "pagination, expected",
    [
        (
            CursorPagination(
                sort=Sort(
                    SortBy.desc("created_at"),
                    SortBy.asc("_id"),
                ),
                per_page=10,
            ),
            [
                {"$sort": {"created_at": -1, "_id": 1}},
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
                    }
                },
            ],
        ),
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
                    }
                },
            ],
        ),
    ],
)
def test_expression(pagination: CursorPagination, expected: ListExpression):
    assert pagination.expression() == expected

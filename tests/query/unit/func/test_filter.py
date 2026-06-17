import pymongo
import pytest

from compose.query.mongo import op
from compose.query.mongo.op import (
    Eq,
    Match,
    Operator,
    SkipNull,
    Sort,
    SortBy,
)


@pytest.mark.parametrize(
    "collection, expected",
    [
        (
            [
                Match.and_(SkipNull(Eq(field="a", value=None))),
                Sort(SortBy(field="a", direction=pymongo.ASCENDING)),
            ],
            [Sort(SortBy(field="a", direction=pymongo.ASCENDING))],
        ),
    ],
)
def test_filter_empty_operator(
    collection: list[Operator],
    expected: list[Operator],
):
    actual = op.func.Filter(collection)

    assert [item.expression() for item in actual] == [item.expression() for item in expected]

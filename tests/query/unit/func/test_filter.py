from collections.abc import Callable

import pymongo
import pytest

from compose.query.mongo import op
from compose.query.mongo.op import (
    EmptyOnNull,
    Eq,
    Match,
    Operator,
    Sort,
    SortBy,
)


@pytest.mark.parametrize(
    "collection, predicate, expected",
    [
        (
            [
                Match.and_(EmptyOnNull(Eq(field="a", value=None))),
                Sort(SortBy(field="a", direction=pymongo.ASCENDING)),
            ],
            op.func.NonEmpty(),
            [Sort(SortBy(field="a", direction=pymongo.ASCENDING))],
        ),
    ],
)
def test_expression(
    collection: list[Operator],
    predicate: Callable[[Operator], bool],
    expected: list[Operator],
):
    actual = op.func.Filter(collection, predicate)

    assert [item.expression() for item in actual] == [item.expression() for item in expected]

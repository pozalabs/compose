import pymongo
import pytest

from compose.query.mongo.op import (
    DictExpression,
    EmptyOnNull,
    Eq,
    Filter,
    Match,
    Operator,
    Sort,
    SortBy,
)


@pytest.fixture
def ops() -> list[Operator]:
    return [
        Match.and_(EmptyOnNull(Eq(field="a", value=None))),
        Sort(SortBy(field="a", direction=pymongo.ASCENDING)),
    ]


@pytest.fixture
def expected() -> list[DictExpression]:
    return [{"$sort": {"a": pymongo.ASCENDING}}]


def test_filter_non_empty_expression(
    ops: list[Operator],
    expected: list[DictExpression],
):
    assert Filter.non_empty(*ops).expression() == expected

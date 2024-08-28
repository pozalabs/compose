from typing import Any

import pymongo
import pytest

import compose


class Item(compose.entity.Entity):
    name: str


@pytest.mark.parametrize(
    "find, expected",
    [
        (
            compose.query.Find[Item]().filter({"name": "item-01"}),
            {"filter": {"name": "item-01"}},
        ),
        (
            compose.query.Find[Item]().filter({"name": "item-01"}).projection({"_id": 1}),
            {"filter": {"name": "item-01"}, "projection": {"_id": 1}},
        ),
        (
            compose.query.Find[Item]()
            .filter({"name": "item-01"})
            .projection({"_id": 1})
            .sort([("name", pymongo.ASCENDING)]),
            {
                "filter": {"name": "item-01"},
                "projection": {"_id": 1},
                "sort": [("name", pymongo.ASCENDING)],
            },
        ),
    ],
)
def test_find_to_query(find: compose.query.Find, expected: dict[str, Any]):
    assert find.to_query() == expected


@pytest.mark.parametrize(
    "find, expected",
    [
        (
            compose.query.Find[Item]().filter({"name": "item-01"}),
            Item,
        ),
        (
            compose.query.Find[Item]().filter({"name": "item-01"}).projection({"_id": 1}),
            dict[str, Any],
        ),
    ],
)
def test_return_type_changes_by_projection(
    find: compose.query.Find, expected: Item | dict[str, Any]
):
    assert find.return_type == expected

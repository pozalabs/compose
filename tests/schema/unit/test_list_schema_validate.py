from typing import Any

import pytest

import compose


class Item(compose.schema.Schema):
    id: int


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            [
                {"id": 1},
                {"id": 2},
            ],
            compose.schema.ListSchema[Item](
                total=2,
                items=[
                    Item(id=1),
                    Item(id=2),
                ],
            ),
        ),
    ],
)
def test_validate(data: list[dict[[str, Any]]], expected: compose.schema.ListSchema[Item]) -> None:
    assert compose.schema.ListSchema[Item](items=data) == expected


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            [
                {"id": 1},
                {"id": 2},
            ],
            compose.schema.ListSchema[Item](
                total=2,
                items=[
                    Item(id=1),
                    Item(id=2),
                ],
            ),
        ),
    ],
)
def test_from_items(
    data: list[dict[[str, Any]]], expected: compose.schema.ListSchema[Item]
) -> None:
    assert compose.schema.ListSchema[Item].from_items(data) == expected

from __future__ import annotations

from typing import Any, Type

import pytest

from compose.pagination import Pagination
from compose.schema import ListSchema, Schema
from compose.types import PyObjectId


class Item(Schema):
    id: PyObjectId


class ListSchemaWithExtra(ListSchema[Item]):
    extra_field: str


class ItemWithCustomParser(Schema):
    id: PyObjectId
    version: str
    is_legacy: bool

    @classmethod
    def from_(cls, data: dict[str, Any]) -> ItemWithCustomParser:
        return cls(
            id=data["id"],
            version=data["version"],
            is_legacy=data["version"] == "v1",
        )


@pytest.fixture
def pagination_without_extra() -> Pagination:
    return Pagination(
        total=2,
        items=[
            dict(id=PyObjectId(b"test-id-0001")),
            dict(id=PyObjectId(b"test-id-0002")),
        ],
    )


@pytest.fixture
def pagination_with_extra() -> Pagination:
    return Pagination(
        total=2,
        items=[
            dict(id=PyObjectId(b"test-id-0001")),
            dict(id=PyObjectId(b"test-id-0002")),
        ],
        extra=dict(extra_field="extra_value"),
    )


@pytest.fixture
def pagination_with_custom_parser() -> Pagination:
    return Pagination(
        total=2,
        items=[
            dict(id=PyObjectId(b"test-id-0001"), version="v1"),
            dict(id=PyObjectId(b"test-id-0002"), version="v2"),
        ],
    )


@pytest.fixture
def expected_without_extra() -> ListSchema[Item]:
    return ListSchema[Item](
        total=2,
        items=[
            Item(id=PyObjectId(b"test-id-0001")),
            Item(id=PyObjectId(b"test-id-0002")),
        ],
    )


@pytest.fixture
def expected_with_extra() -> ListSchemaWithExtra:
    return ListSchemaWithExtra(
        total=2,
        items=[
            Item(id=PyObjectId(b"test-id-0001")),
            Item(id=PyObjectId(b"test-id-0002")),
        ],
        extra_field="extra_value",
    )


@pytest.fixture
def expected_with_custom_parser() -> ListSchema[ItemWithCustomParser]:
    return ListSchema[ItemWithCustomParser](
        total=2,
        items=[
            ItemWithCustomParser(id=PyObjectId(b"test-id-0001"), version="v1", is_legacy=True),
            ItemWithCustomParser(id=PyObjectId(b"test-id-0002"), version="v2", is_legacy=False),
        ],
    )


@pytest.mark.parametrize(
    "schema_type, from_pagination_kwargs, pagination, expected",
    [
        (
            ListSchema[Item],
            {},
            "pagination_without_extra",
            "expected_without_extra",
        ),
        (
            ListSchemaWithExtra,
            {},
            "pagination_with_extra",
            "expected_with_extra",
        ),
        (
            ListSchema[ItemWithCustomParser],
            dict(parser_name="from_"),
            "pagination_with_custom_parser",
            "expected_with_custom_parser",
        ),
    ],
    ids=(
        "스키마에 추가 필드를 정의하지 않으면 기본 필드만 매핑",
        "스키마에 추가 필드를 정의하면 `Pagination.extra`를 추가 필드로 매핑",
        "별도로 정의한 파서 메서드명을 입력하면 스키마의 해당 메서드를 사용해 파싱",
    ),
)
def test_from_pagination(
    schema_type: Type[ListSchema[Item]],
    from_pagination_kwargs: dict[str, Any],
    pagination: str,
    expected: str,
    request: pytest.FixtureRequest,
):
    pagination: Pagination = request.getfixturevalue(pagination)
    expected: ListSchema[Item] = request.getfixturevalue(expected)

    actual = schema_type.from_pagination(pagination, **from_pagination_kwargs)

    assert actual == expected

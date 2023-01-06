from typing import Type

import pytest

from compose.pagination import Pagination
from compose.schema import ListSchema, Schema
from compose.types import PyObjectId


class Item(Schema):
    id: PyObjectId


class ListSchemaWithExtra(ListSchema[Item]):
    extra_field: str


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


@pytest.mark.parametrize(
    "schema_type, pagination, expected",
    [
        (
            ListSchema[Item],
            "pagination_without_extra",
            "expected_without_extra",
        ),
        (
            ListSchemaWithExtra,
            "pagination_with_extra",
            "expected_with_extra",
        ),
    ],
    ids=(
        "스키마에 추가 필드를 정의하지 않으면 기본 필드만 매핑",
        "스키마에 추가 필드를 정의하면 `Pagination.extra`를 추가 필드로 매핑",
    ),
)
def test_from_pagination_by_extra(
    schema_type: Type[ListSchema[Item]],
    pagination: str,
    expected: str,
    request: pytest.FixtureRequest,
):
    pagination: Pagination = request.getfixturevalue(pagination)
    expected: ListSchema[Item] = request.getfixturevalue(expected)

    actual = schema_type.from_pagination(pagination)

    assert actual == expected

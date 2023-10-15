from __future__ import annotations

from typing import Any

import pytest

import compose


class Item(compose.schema.Schema):
    id: compose.types.PyObjectId


class ListSchemaWithExtra(compose.schema.ListSchema[Item]):
    extra_field: str


class ItemWithCustomParser(compose.schema.Schema):
    id: compose.types.PyObjectId
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
def pagination_without_extra() -> compose.pagination.Pagination:
    return compose.pagination.Pagination(
        total=2,
        items=[
            dict(id=compose.types.PyObjectId(b"test-id-0001")),
            dict(id=compose.types.PyObjectId(b"test-id-0002")),
        ],
    )


@pytest.fixture
def pagination_with_extra() -> compose.pagination.Pagination:
    return compose.pagination.Pagination(
        total=2,
        items=[
            dict(id=compose.types.PyObjectId(b"test-id-0001")),
            dict(id=compose.types.PyObjectId(b"test-id-0002")),
        ],
        extra=dict(extra_field="extra_value"),
    )


@pytest.fixture
def pagination_with_custom_parser() -> compose.pagination.Pagination:
    return compose.pagination.Pagination(
        total=2,
        items=[
            dict(id=compose.types.PyObjectId(b"test-id-0001"), version="v1"),
            dict(id=compose.types.PyObjectId(b"test-id-0002"), version="v2"),
        ],
    )


@pytest.fixture
def expected_without_extra() -> compose.schema.ListSchema[Item]:
    return compose.schema.ListSchema[Item](
        total=2,
        items=[
            Item(id=compose.types.PyObjectId(b"test-id-0001")),
            Item(id=compose.types.PyObjectId(b"test-id-0002")),
        ],
    )


@pytest.fixture
def expected_with_extra() -> ListSchemaWithExtra:
    return ListSchemaWithExtra(
        total=2,
        items=[
            Item(id=compose.types.PyObjectId(b"test-id-0001")),
            Item(id=compose.types.PyObjectId(b"test-id-0002")),
        ],
        extra_field="extra_value",
    )


@pytest.fixture
def expected_with_custom_parser() -> compose.schema.ListSchema[ItemWithCustomParser]:
    return compose.schema.ListSchema[ItemWithCustomParser](
        total=2,
        items=[
            ItemWithCustomParser(
                id=compose.types.PyObjectId(b"test-id-0001"), version="v1", is_legacy=True
            ),
            ItemWithCustomParser(
                id=compose.types.PyObjectId(b"test-id-0002"), version="v2", is_legacy=False
            ),
        ],
    )


@pytest.mark.parametrize(
    "schema_type, from_pagination_kwargs, pagination, expected",
    [
        (
            compose.schema.ListSchema[Item],
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
            compose.schema.ListSchema[ItemWithCustomParser],
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
    schema_type: type[compose.schema.ListSchema[Item]],
    from_pagination_kwargs: dict[str, Any],
    pagination: str,
    expected: str,
    request: pytest.FixtureRequest,
):
    pagination: compose.pagination.Pagination = request.getfixturevalue(pagination)
    expected: compose.schema.ListSchema[Item] = request.getfixturevalue(expected)

    actual = schema_type.from_pagination(pagination, **from_pagination_kwargs)

    assert actual == expected


@pytest.mark.parametrize(
    "schema_type, parser_name, pagination",
    [
        (
            compose.schema.ListSchema[Item],
            "undefined_parser",
            "pagination_without_extra",
        ),
    ],
    ids=("스키마에 정의되어 있지 않은 파서를 입력하면 오류가 발생",),
)
def test_from_pagination_with_undefined_parser(
    schema_type: type[compose.schema.ListSchema[Item]],
    parser_name: str,
    pagination: str,
    request: pytest.FixtureRequest,
):
    pagination: compose.pagination.Pagination = request.getfixturevalue(pagination)

    with pytest.raises(AttributeError):
        schema_type.from_pagination(
            pagination=pagination,
            parser_name=parser_name,
        )

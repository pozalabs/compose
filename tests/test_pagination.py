from collections.abc import Callable
from typing import Any

import pytest

from compose.pagination import CursorPaginationResult, OffsetPaginationResult

PaginationFactory = Callable[..., OffsetPaginationResult]


@pytest.fixture
def pagination_factory() -> PaginationFactory:
    def inner(
        num_items: int = 5,
        page: int = 1,
        per_page: int = 10,
    ) -> OffsetPaginationResult:
        return OffsetPaginationResult(
            total=num_items,
            items=list(range(num_items)),
            page=page,
            per_page=per_page,
        )

    return inner


@pytest.mark.parametrize(
    "pagination_params, expected",
    [
        (
            dict(
                num_items=4,
                page=1,
                per_page=2,
            ),
            2,
        ),
        (
            dict(
                num_items=4,
                page=1,
                per_page=3,
            ),
            2,
        ),
    ],
    ids=(
        "목록 개수가 per_page로 나누어 떨어지는 경우",
        "목록 개수가 per_page로 나누어 떨어지지 않는 경우",
    ),
)
def test_pages(
    pagination_factory: PaginationFactory,
    pagination_params: dict[str, Any],
    expected: int,
):
    pagination = pagination_factory(**pagination_params)

    assert pagination.pages == expected


@pytest.mark.parametrize(
    "pagination_params, expected",
    [
        (
            dict(
                num_items=4,
                page=1,
                per_page=2,
            ),
            None,
        ),
        (
            dict(
                num_items=4,
                page=2,
                per_page=2,
            ),
            1,
        ),
    ],
    ids=(
        "현재 page가 첫번째 page인 경우",
        "현재 page가 첫번째 page가 아닌 경우",
    ),
)
def test_prev_page(
    pagination_factory: PaginationFactory,
    pagination_params: dict[str, Any],
    expected: int | None,
):
    pagination = pagination_factory(**pagination_params)

    assert pagination.prev_page == expected


@pytest.mark.parametrize(
    "pagination_params, expected",
    [
        (
            dict(
                num_items=4,
                page=2,
                per_page=2,
            ),
            None,
        ),
        (
            dict(
                num_items=4,
                page=1,
                per_page=2,
            ),
            2,
        ),
    ],
    ids=(
        "현재 page가 마지막 page인 경우",
        "현재 page가 마지막 page가 아닌 경우",
    ),
)
def test_next_page(
    pagination_factory: PaginationFactory,
    pagination_params: dict[str, Any],
    expected: int | None,
):
    pagination = pagination_factory(**pagination_params)

    assert pagination.next_page == expected


@pytest.mark.parametrize(
    "pagination, expected",
    [
        (OffsetPaginationResult(total=0, items=[], page=1, per_page=10), True),
        (OffsetPaginationResult(total=1, items=["item"], page=1, per_page=10), False),
    ],
    ids=(
        "페이지네이션 목록이 비어 있으면 `True`를 리턴한다.",
        "페이지네이션 목록이 비어 있지 않으면 `False`를 리턴한다.",
    ),
)
def test_is_empty(pagination: OffsetPaginationResult, expected: bool):
    assert pagination.is_empty is expected


def test_cursor_pagination_result_empty():
    result = CursorPaginationResult.empty()

    assert result == CursorPaginationResult(items=[], next_cursor=None)

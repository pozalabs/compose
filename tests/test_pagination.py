from typing import Any, Callable, Optional

import pytest

from compose.pagination import Pagination

PaginationFactory = Callable[..., Pagination]


@pytest.fixture
def pagination_factory() -> PaginationFactory:
    def inner(
        num_items: int = 5,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Pagination:
        return Pagination(
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
            dict(num_items=4),
            1,
        ),
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
        "page, per_page를 None으로 입력하는 경우",
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
            dict(num_items=4),
            None,
        ),
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
        "page, per_page를 None으로 입력하는 경우",
        "현재 page가 첫번째 page인 경우",
        "현재 page가 첫번째 page가 아닌 경우",
    ),
)
def test_prev_page(
    pagination_factory: PaginationFactory,
    pagination_params: dict[str, Any],
    expected: Optional[int],
):
    pagination = pagination_factory(**pagination_params)

    assert pagination.prev_page == expected


@pytest.mark.parametrize(
    "pagination_params, expected",
    [
        (
            dict(num_items=4),
            None,
        ),
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
        "page, per_page를 None으로 입력하는 경우",
        "현재 page가 마지막 page인 경우",
        "현재 page가 마지막 page가 아닌 경우",
    ),
)
def test_next_page(
    pagination_factory: PaginationFactory,
    pagination_params: dict[str, Any],
    expected: Optional[int],
):
    pagination = pagination_factory(**pagination_params)

    assert pagination.next_page == expected

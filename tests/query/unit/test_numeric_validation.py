import pytest

from compose.query.mongo.op import CursorPagination, Limit, OffsetPagination, Sample, Skip, Sort
from compose.query.mongo.op.sort import SortBy


def test_cannot_create_skip_with_negative():
    with pytest.raises(ValueError):
        Skip(-1)


@pytest.mark.parametrize("value", [0, -1])
def test_cannot_create_limit_with_non_positive(value: int):
    with pytest.raises(ValueError):
        Limit(value)


def test_cannot_create_sample_with_negative():
    with pytest.raises(ValueError):
        Sample(-1)


def test_cannot_create_offset_pagination_with_non_positive_page():
    with pytest.raises(ValueError):
        OffsetPagination(page=0, per_page=10)


def test_cannot_create_offset_pagination_with_non_positive_per_page():
    with pytest.raises(ValueError):
        OffsetPagination(page=1, per_page=0)


def test_cannot_create_cursor_pagination_with_non_positive_per_page():
    with pytest.raises(ValueError):
        CursorPagination(
            sort=Sort(SortBy.desc("_id")),
            per_page=0,
        )

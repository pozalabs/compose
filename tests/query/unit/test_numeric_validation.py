import pytest

from compose.query.mongo.op import CursorPagination, Limit, OffsetPagination, Sample, Skip, Sort
from compose.query.mongo.op.sort import SortBy


class TestSkipRejectNegative:
    def test_reject_negative(self):
        with pytest.raises(ValueError):
            Skip(-1)


class TestLimitRejectNonPositive:
    @pytest.mark.parametrize("value", [0, -1])
    def test_reject_non_positive(self, value: int):
        with pytest.raises(ValueError):
            Limit(value)


class TestSampleRejectNegative:
    def test_reject_negative(self):
        with pytest.raises(ValueError):
            Sample(-1)


class TestOffsetPaginationRejectInvalid:
    def test_reject_non_positive_page(self):
        with pytest.raises(ValueError):
            OffsetPagination(page=0, per_page=10)

    def test_reject_non_positive_per_page(self):
        with pytest.raises(ValueError):
            OffsetPagination(page=1, per_page=0)


class TestCursorPaginationRejectInvalid:
    def test_reject_non_positive_per_page(self):
        with pytest.raises(ValueError):
            CursorPagination(
                sort=Sort(SortBy.desc("_id")),
                per_page=0,
            )

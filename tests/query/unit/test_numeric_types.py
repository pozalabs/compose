import pytest

from compose.query.mongo.op.types import _NonNegativeInt, _PositiveInt


class TestNonNegativeInt:
    @pytest.mark.parametrize("value", [0, 1, 100])
    def test_accept_non_negative(self, value: int):
        assert _NonNegativeInt(value) == value

    def test_reject_negative(self):
        with pytest.raises(ValueError):
            _NonNegativeInt(-1)


class TestPositiveInt:
    @pytest.mark.parametrize("value", [1, 100])
    def test_accept_positive(self, value: int):
        assert _PositiveInt(value) == value

    @pytest.mark.parametrize("value", [0, -1])
    def test_reject_non_positive(self, value: int):
        with pytest.raises(ValueError):
            _PositiveInt(value)

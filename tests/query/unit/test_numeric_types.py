import pytest

from compose.query.mongo.op.types import _NonNegativeInt, _PositiveInt


@pytest.mark.parametrize("value", [0, 1, 100])
def test_non_negative_int(value: int):
    assert _NonNegativeInt(value) == value


def test_cannot_create_negative_non_negative_int():
    with pytest.raises(ValueError):
        _NonNegativeInt(-1)


@pytest.mark.parametrize("value", [1, 100])
def test_positive_int(value: int):
    assert _PositiveInt(value) == value


@pytest.mark.parametrize("value", [0, -1])
def test_cannot_create_non_positive_positive_int(value: int):
    with pytest.raises(ValueError):
        _PositiveInt(value)

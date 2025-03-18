import pytest

import compose


@pytest.mark.parametrize(
    "hours, expected",
    [
        (1, 3600),
        (1.5, 5400),
        (2, 7200),
        (1.25, 4500),
    ],
)
def test_from_hours(hours: float, expected: compose.types.Seconds):
    assert compose.types.Seconds.from_hours(hours) == expected


@pytest.mark.parametrize(
    "minutes, expected",
    [
        (1, 60),
        (1.5, 90),
        (2, 120),
        (1.25, 75),
    ],
)
def test_from_minutes(minutes: float, expected: compose.types.Seconds):
    assert compose.types.Seconds.from_minutes(minutes) == expected


def test_cannot_create_negative_seconds():
    with pytest.raises(ValueError):
        compose.types.Seconds(-1)

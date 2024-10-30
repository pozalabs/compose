from collections.abc import Callable

import pendulum
import pytest

import compose


@pytest.mark.parametrize(
    "date_range_factory, expected",
    [
        (
            lambda: compose.types.DateRange.day_of(dt=pendulum.datetime(2024, 10, 10, 10, 10)),
            compose.types.DateRange(
                start=pendulum.datetime(2024, 10, 10),
                end=pendulum.datetime(2024, 10, 11),
            ),
        ),
        (
            lambda: compose.types.DateRange.day_of(
                dt=pendulum.datetime(2024, 10, 10, 8, tz="Asia/Seoul"),
                tz=pendulum.UTC,
            ),
            compose.types.DateRange(
                start=pendulum.datetime(2024, 10, 9, 15),
                end=pendulum.datetime(2024, 10, 10, 15),
            ),
        ),
        (
            lambda: compose.types.DateRange.day_of(
                dt=pendulum.datetime(2024, 10, 10, 8, tz="Asia/Seoul"),
                tz="Asia/Seoul",
            ),
            compose.types.DateRange(
                start=pendulum.datetime(2024, 10, 10, tz="Asia/Seoul"),
                end=pendulum.datetime(2024, 10, 11, tz="Asia/Seoul"),
            ),
        ),
    ],
    ids=(
        "UTC 날짜를 입력하는 경우 UTC 기준 시작 시간을 시작 시간으로 사용한다.",
        "UTC 외의 날짜를 입력하는 경우 해당 타임존 기준 시작 시간을 UTC로 변환한 시간을 시작 시간으로 사용한다.",
        "UTC 외의 날짜를 입력하고 타임존을 설정하는 경우 해당 타임존에서 계산한 시간을 시작 시간으로 사용한다.",
    ),
)
def test_day_of(
    date_range_factory: Callable[[], compose.types.DateRange],
    expected: compose.types.DateRange,
):
    assert date_range_factory() == expected

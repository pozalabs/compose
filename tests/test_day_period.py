import pendulum
import pytest

import compose


@pytest.mark.parametrize(
    "dt, expected",
    [
        (
            pendulum.datetime(2024, 10, 10, 10, 10),
            compose.DayPeriod(
                start=pendulum.datetime(2024, 10, 10),
                end=pendulum.datetime(2024, 10, 11),
            ),
        ),
        (
            pendulum.datetime(2024, 10, 10, 8, tz="Asia/Seoul"),
            compose.DayPeriod(
                start=pendulum.datetime(2024, 10, 9, 15),
                end=pendulum.datetime(2024, 10, 10, 15),
            ),
        ),
    ],
    ids=(
        "UTC 날짜를 입력하는 경우 UTC 기준 시작 시간을 시작 시간으로 사용한다.",
        "UTC 외의 날짜를 입력하는 경우 해당 타임존 기준 시작 시간을 UTC로 변환한 시각을 시작 시간으로 사용한다.",
    ),
)
def test_for_day(dt: pendulum.DateTime, expected: compose.DayPeriod):
    assert compose.DayPeriod.for_day(dt) == expected

import datetime
from typing import Union

import pendulum
import pytest
from pendulum.tz.timezone import Timezone

from compose.container import BaseModel
from compose.types import DateTime


class Model(BaseModel):
    created_at: DateTime


@pytest.fixture
def model(request: pytest.FixtureRequest) -> Model:
    dt: Union[datetime.datetime, pendulum.DateTime] = getattr(request, "param")
    return Model(created_at=dt)


@pytest.fixture
def expected(request: pytest.FixtureRequest) -> Model:
    dt: Union[pendulum.DateTime, DateTime] = getattr(request, "param")
    return Model(created_at=dt)


@pytest.mark.parametrize(
    "model, expected",
    [
        (
            datetime.datetime(2023, 1, 5),
            pendulum.datetime(2023, 1, 5, tz=pendulum.UTC),
        ),
        (
            datetime.datetime(2023, 1, 5, tzinfo=Timezone("Asia/Seoul")),
            pendulum.datetime(2023, 1, 5, tz=Timezone("Asia/Seoul")),
        ),
        (
            pendulum.datetime(2023, 1, 5, tz=pendulum.UTC),
            DateTime(2023, 1, 5, tzinfo=pendulum.UTC),
        ),
    ],
    ids=(
        "naive datetime 객체는 UTC DateTime으로 파싱",
        "aware datetime 객체는 동일한 타임존의 DateTime으로 파싱",
        "DateTime 객체는 DateTime 객체를 그대로 리턴",
    ),
    indirect=["model", "expected"],
)
def test_datetime_instantiate(model: Model, expected: Model):
    assert model == expected

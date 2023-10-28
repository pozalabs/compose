from __future__ import annotations

import datetime
from collections.abc import Callable, Generator
from typing import Any, Union

import pendulum
from pydantic.datetime_parse import parse_datetime


class DateTime(pendulum.DateTime):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], pendulum.DateTime], None, None]:
        yield parse_datetime  # type: ignore
        yield cls._instance

    @classmethod
    def _instance(cls, v: Union[datetime.datetime, pendulum.DateTime]) -> pendulum.DateTime:
        return pendulum.instance(dt=v, tz=pendulum.UTC)

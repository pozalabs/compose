from __future__ import annotations

import datetime
from collections.abc import Callable, Generator
from typing import Any

import pendulum
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema

from .helper import get_pydantic_core_schema


class DateTime(pendulum.DateTime):
    """https://stackoverflow.com/a/76719893"""

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], pendulum.DateTime], None, None]:
        yield cls._instance

    @classmethod
    def _instance(cls, v: datetime.datetime | pendulum.DateTime) -> pendulum.DateTime:
        return pendulum.instance(obj=v, tz=pendulum.UTC)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return get_pydantic_core_schema(cls, handler(datetime.datetime))

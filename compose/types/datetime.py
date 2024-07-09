from __future__ import annotations

import datetime
from collections.abc import Callable, Generator
from typing import Any

import pendulum

from .. import compat
from .helper import chain

if compat.IS_PYDANTIC_V2:
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import CoreSchema, core_schema
else:
    from pydantic.datetime_parse import parse_datetime


class DateTime(pendulum.DateTime):
    """https://stackoverflow.com/a/76719893"""

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], pendulum.DateTime], None, None]:
        if not compat.IS_PYDANTIC_V2:
            yield parse_datetime
        yield cls._instance

    @classmethod
    def _instance(cls, v: datetime.datetime | pendulum.DateTime) -> pendulum.DateTime:
        return pendulum.instance(obj=v, tz=pendulum.UTC)

    if compat.IS_PYDANTIC_V2:

        @classmethod
        def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: GetCoreSchemaHandler
        ) -> CoreSchema:
            return core_schema.no_info_after_validator_function(
                chain(*cls.__get_validators__()),
                handler(datetime.datetime),
            )

from __future__ import annotations

import datetime
from collections.abc import Callable, Generator
from typing import Any, Union

import pendulum

from .. import compat

if compat.IS_PYDANTIC_V2:
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import CoreSchema, core_schema
else:
    from pydantic.datetime_parse import parse_datetime


class DateTime(pendulum.DateTime):
    """https://stackoverflow.com/a/76719893"""

    if compat.IS_PYDANTIC_V2:

        @classmethod
        def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: GetCoreSchemaHandler
        ) -> CoreSchema:
            return core_schema.no_info_after_validator_function(
                cls._instance,
                handler(datetime.datetime),
            )

    else:

        @classmethod
        def __get_validators__(cls) -> Generator[Callable[[Any], pendulum.DateTime], None, None]:
            yield parse_datetime
            yield cls._instance

    @classmethod
    def _instance(cls, v: Union[datetime.datetime, pendulum.DateTime]) -> pendulum.DateTime:
        return pendulum.instance(dt=v, tz=pendulum.UTC)

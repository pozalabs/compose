from __future__ import annotations

import datetime
from typing import Any, Union

import pendulum
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class DateTime(pendulum.DateTime):
    """https://stackoverflow.com/a/76719893"""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._instance,
            handler(datetime.datetime),
        )

    @classmethod
    def _instance(cls, v: Union[datetime.datetime, pendulum.DateTime]) -> pendulum.DateTime:
        return pendulum.instance(dt=v, tz=pendulum.UTC)

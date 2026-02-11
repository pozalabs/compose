import datetime
from dataclasses import dataclass
from typing import Any, Self

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
            cls._validate, handler(datetime.datetime)
        )

    @classmethod
    def _validate(cls, v: datetime.datetime) -> pendulum.DateTime:
        return pendulum.instance(obj=v, tz=pendulum.UTC)


@dataclass
class DateRange:
    start: pendulum.DateTime
    end: pendulum.DateTime

    @classmethod
    def day_of(
        cls,
        dt: pendulum.DateTime,
        tz: pendulum.tz.Timezone | str = pendulum.UTC,
    ) -> Self:
        if dt.tzinfo is None:
            raise ValueError("input datetime must be aware")

        return cls(start=(start := dt.start_of("day").in_tz(tz)), end=start.add(days=1))

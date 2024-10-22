from typing import Self

import pendulum

from . import container, types


class DateRange(container.BaseModel):
    start: types.DateTime
    end: types.DateTime

    @classmethod
    def from_day_start(
        cls,
        dt: pendulum.DateTime,
        tz: pendulum.tz.Timezone = pendulum.UTC,
    ) -> Self:
        if dt.tzinfo is None:
            raise ValueError("input datetime must be aware")

        return cls(start=(start := dt.start_of("day").in_tz(tz)), end=start.add(days=1))

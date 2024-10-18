from typing import Self

import pendulum

from . import container


class DayPeriod(container.BaseModel):
    start: pendulum.DateTime
    end: pendulum.DateTime

    @classmethod
    def for_day(cls, dt: pendulum.DateTime, tz: pendulum.tz.Timezone = pendulum.UTC) -> Self:
        if dt.tzinfo is None:
            raise ValueError("input datetime must be aware")

        return cls(start=(start := dt.start_of("day").in_tz(tz)), end=start.add(days=1))

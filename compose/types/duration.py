from typing import Any, Self

from . import primitive

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 60 * SECONDS_PER_MINUTE


class Seconds(primitive.Int):
    def __new__(cls, v: Any, /) -> Self:
        v = super().__new__(cls, v)
        if v < 0:
            raise ValueError("`Seconds` must be a non-negative integer")
        return v

    @classmethod
    def from_hours(cls, hours: float) -> Self:
        return cls(hours * SECONDS_PER_HOUR)

    @classmethod
    def from_minutes(cls, minutes: float) -> Self:
        return cls(minutes * SECONDS_PER_MINUTE)

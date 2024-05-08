import enum

import compose


class Status(enum.StrEnum):
    PENDING = enum.auto()
    RUNNING = enum.auto()
    COMPLETED = enum.auto()
    FAILED = enum.auto()

    @property
    def is_active(self) -> bool:
        return self in (Status.PENDING, Status.RUNNING)


test_status_is_active = compose.testing.create_enum_flag_property_test(
    Status,
    Status.is_active.fget,
    truthy={Status.PENDING, Status.RUNNING},
)

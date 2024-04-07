import enum
from typing import Any, Self


class AppEnv(enum.StrEnum):
    TEST = enum.auto()
    LOCAL = enum.auto()
    DEV = enum.auto()
    STG = enum.auto()
    PRD = enum.auto()

    @classmethod
    def from_env(cls, env: str) -> Self:
        if env is None or env not in set(enum_values(cls)):
            raise ValueError(f"Invalid value for {cls.__name__}: {env}")

        return cls(env)


def enum_values(e: type[enum.Enum], /) -> list[Any]:
    return [member.value for _, member in e.__members__.items()]

import enum
from typing import Any


def openapi_tags(tag: type[enum.StrEnum]) -> list[dict[str, Any]]:
    return [{"name": member.value} for member in tag.__members__.values()]

import enum
from typing import Any

from compose import schema


def openapi_tags(tag: type[enum.StrEnum]) -> list[dict[str, Any]]:
    return [{"name": member.value} for member in tag.__members__.values()]


def additional_responses(*status_codes: int) -> dict[int, dict[str, Any]]:
    return {int(status_code): {"model": schema.Schema} for status_code in sorted(status_codes)}

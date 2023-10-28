from __future__ import annotations

import json
from typing import Any, Optional, TypeVar, Union

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict

from . import field, types

IncEx = Union[set[int], set[str], dict[int, Any], dict[str, Any], None]
AbstractSetIntStr = Union[set[int], set[str]]
MappingIntStrAny = Union[dict[int, Any], dict[str, Any]]
Model = TypeVar("Model", bound=PydanticBaseModel)


class BaseModel(PydanticBaseModel):
    def copy(
        self,
        *,
        include: Optional[Union[AbstractSetIntStr, MappingIntStrAny]] = None,
        exclude: Optional[Union[AbstractSetIntStr, MappingIntStrAny]] = None,
        update: Optional[dict[str, Any]] = None,
        deep: bool = False,
    ) -> Model:
        return super().model_copy(update=update, deep=deep)

    def encode(
        self,
        *,
        indent: Optional[int] = None,
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> dict[str, Any]:
        return json.loads(
            self.model_dump_json(
                indent=indent,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                round_trip=round_trip,
                warnings=warnings,
            )
        )

    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="ignore",
    )


class TimeStampedModel(BaseModel):
    created_at: types.DateTime = field.DateTimeField()
    updated_at: types.DateTime = field.DateTimeField()

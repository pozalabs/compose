from __future__ import annotations

import copy
import json
from typing import Any, Optional, TypeVar, Union

import bson
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Extra

from . import field, types

IncEx = Union[set[int], set[str], dict[int, Any], dict[str, Any], None]
AbstractSetIntStr = Union[set[int], set[str]]
MappingIntStrAny = Union[dict[int, Any], dict[str, Any]]
Model = TypeVar("Model", bound=PydanticBaseModel)


class BaseModel(PydanticBaseModel):
    def copy(
        self,
        *,
        include: AbstractSetIntStr | MappingIntStrAny | None = None,
        exclude: AbstractSetIntStr | MappingIntStrAny | None = None,
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
        json_encoders={bson.ObjectId: str},
        populate_by_name=True,
        validate_assignment=True,
        extra=Extra.forbid,
    )


class TimeStampedModel(BaseModel):
    created_at: types.DateTime = field.DateTimeField()
    updated_at: types.DateTime = field.DateTimeField()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        model_fields = copy.deepcopy(cls.model_fields)

        created_at_field = model_fields.pop("created_at")
        updated_at_field = model_fields.pop("updated_at")
        cls.model_fields = model_fields | dict(
            created_at=created_at_field,
            updated_at=updated_at_field,
        )

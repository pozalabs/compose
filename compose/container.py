from __future__ import annotations

import json
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar

import bson
from pydantic import BaseModel as PydanticBaseModel

from . import compat, field, types

if compat.IS_PYDANTIC_V2:
    from pydantic import ConfigDict

    AbstractSetIntStr: TypeAlias = set[int] | set[str]
    MappingIntStrAny: TypeAlias = dict[int, Any] | dict[str, Any]
else:
    if TYPE_CHECKING:
        from pydantic.typing import AbstractSetIntStr, DictStrAny, MappingIntStrAny

IncEx: TypeAlias = set[int] | set[str] | dict[int, Any] | dict[str, Any] | None
Model = TypeVar("Model", bound=PydanticBaseModel)


class BaseModel(PydanticBaseModel):
    if compat.IS_PYDANTIC_V2:

        def copy(
            self,
            *,
            include: AbstractSetIntStr | MappingIntStrAny | None = None,
            exclude: AbstractSetIntStr | MappingIntStrAny | None = None,
            update: dict[str, Any] | None = None,
            deep: bool = False,
        ) -> Model:
            return super().model_copy(update=update, deep=deep)

        def encode(
            self,
            *,
            indent: int | None = None,
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

    else:

        def copy(
            self,
            *,
            include: AbstractSetIntStr | MappingIntStrAny | None = None,
            exclude: AbstractSetIntStr | MappingIntStrAny | None = None,
            update: DictStrAny | None = None,
            deep: bool = False,
            strict: bool = True,
        ) -> BaseModel:
            if strict and (diff := set((update or {}).keys()) - set(self.__fields__.keys())):
                raise AttributeError(
                    f"{self.__class__.__name__} has no attributes: {', '.join(diff)}"
                )

            return super().copy(
                include=include,
                exclude=exclude,
                update=update,
                deep=deep,
            )

        def encode(
            self,
            *,
            include: AbstractSetIntStr | MappingIntStrAny | None = None,
            exclude: AbstractSetIntStr | MappingIntStrAny | None = None,
            by_alias: bool = False,
            skip_defaults: bool | None = None,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            encoder: Callable[[Any], Any] | None = None,
            models_as_dict: bool = True,
            **dumps_kwargs: Any,
        ) -> dict[str, Any]:
            return json.loads(
                self.json(
                    include=include,
                    exclude=exclude,
                    by_alias=by_alias,
                    skip_defaults=skip_defaults,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                    encoder=encoder,
                    models_as_dict=models_as_dict,
                    **dumps_kwargs,
                )
            )

        class Config:
            json_encoders = {bson.ObjectId: str}
            allow_population_by_field_name = True
            validate_assignment = True


class TimeStampedModel(BaseModel):
    created_at: types.DateTime = field.DateTimeField()
    updated_at: types.DateTime = field.DateTimeField()

    if not compat.IS_PYDANTIC_V2:

        def __init_subclass__(cls, **kwargs: Any) -> None:
            super().__init_subclass__(**kwargs)

            created_at_field = cls.__fields__.pop("created_at")
            updated_at_field = cls.__fields__.pop("updated_at")
            cls.__fields__ |= dict(created_at=created_at_field, updated_at=updated_at_field)

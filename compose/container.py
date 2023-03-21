from __future__ import annotations

import json
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Optional, Union

import bson
from pydantic import BaseModel as PydanticBaseModel

from . import field, types

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, DictStrAny, MappingIntStrAny


class BaseModel(PydanticBaseModel):
    def copy(
        self,
        *,
        include: Optional[Union[AbstractSetIntStr, MappingIntStrAny]] = None,
        exclude: Optional[Union[AbstractSetIntStr, MappingIntStrAny]] = None,
        update: Optional[DictStrAny] = None,
        deep: bool = False,
        strict: bool = True,
    ) -> BaseModel:
        if strict and (diff := set((update or {}).keys()) - set(self.__fields__.keys())):
            raise AttributeError(f"{self.__class__.__name__} has no attributes: {', '.join(diff)}")

        return super().copy(
            include=include,
            exclude=exclude,
            update=update,
            deep=deep,
        )

    def encode(
        self,
        *,
        include: Optional[Union[AbstractSetIntStr, MappingIntStrAny]] = None,
        exclude: Optional[Union[AbstractSetIntStr, MappingIntStrAny]] = None,
        by_alias: bool = False,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encoder: Optional[Callable[[Any], Any]] = None,
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

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        created_at_field = cls.__fields__.pop("created_at")
        updated_at_field = cls.__fields__.pop("updated_at")
        cls.__fields__ |= dict(created_at=created_at_field, updated_at=updated_at_field)

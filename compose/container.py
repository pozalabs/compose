from __future__ import annotations

from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict
from typing_extensions import Self

from . import field, types


class BaseModel(PydanticBaseModel):
    @classmethod
    def from_model(cls, model: BaseModel) -> Self:
        return cls.model_validate(model.model_dump())

    def validated_copy(
        self,
        *,
        update: dict[str, Any] | None = None,
        deep: bool = False,
    ) -> Self:
        result = self.model_copy(update=update, deep=deep)
        return self.__class__.model_validate(result.model_dump())

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="ignore",
    )


class TimeStampedModel(BaseModel):
    created_at: types.DateTime = field.DateTimeField()
    updated_at: types.DateTime = field.DateTimeField()

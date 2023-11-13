from typing import Any, ClassVar, TypeVar

from pydantic import BaseModel

from . import compat, container, field, types

ModelType = TypeVar("ModelType", bound=BaseModel)


class Entity(container.TimeStampedModel):
    id: types.PyObjectId = field.IdField(default_factory=types.PyObjectId)

    updatable_fields: ClassVar[set[str]] = set()

    if compat.IS_PYDANTIC_V2:

        @classmethod
        def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
            super().__pydantic_init_subclass__(**kwargs)

            fields = set(cls.model_fields.keys())
            if diff := set(cls.updatable_fields) - fields:
                raise ValueError(f"`updatable_fields` must be subset of {fields}, but got {diff}")

    else:

        def __init_subclass__(cls, **kwargs: Any) -> None:
            super().__init_subclass__(**kwargs)

            fields = set(cls.__fields__.keys())
            if diff := set(cls.updatable_fields) - fields:
                raise ValueError(f"`updatable_fields` must be subset of {fields}, but got {diff}")

            id_field = cls.__fields__.pop("id")
            cls.__fields__ = dict(id=id_field) | cls.__fields__

    def update(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if key not in self.updatable_fields:
                continue

            setattr(self, key, value)

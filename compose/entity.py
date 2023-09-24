from typing import Any, ClassVar

from . import container, field, types


class Entity(container.TimeStampedModel):
    id: types.PyObjectId = field.IdField(default_factory=types.PyObjectId)

    updatable_fields: ClassVar[set[str]] = set()

    def update(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if key not in self.updatable_fields:
                continue

            setattr(self, key, value)

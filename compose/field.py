from collections.abc import Callable
from typing import Any, Optional

import pendulum
from pydantic import Field
from pydantic.fields import FieldInfo

from . import types


class _IdField:
    def __call__(self, alias: Optional[str] = None, **kwargs) -> FieldInfo:
        return Field(alias=alias or "_id", **kwargs)


class _DatetimeField:
    def __call__(self, **kwargs) -> types.DateTime:
        return Field(default_factory=pendulum.DateTime.utcnow, **kwargs)


IdField: Callable[..., Any] = _IdField()
DateTimeField: Callable[..., types.DateTime] = _DatetimeField()

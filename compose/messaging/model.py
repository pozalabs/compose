from typing import Any

from pydantic import SerializeAsAny, SkipValidation

from compose import container
from compose.event import Event


class EventMessage(container.BaseModel):
    body: SerializeAsAny[SkipValidation[Event[Any]]]


class SqsEventMessage(EventMessage):
    receipt_handle: str

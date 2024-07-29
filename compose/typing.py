from collections.abc import Callable, Generator
from typing import Any, Self, TypeAlias, TypeVar

from .types import PyObjectId

T = TypeVar("T")

Validator: TypeAlias = Callable[[Any], Self]
ValidatorGenerator: TypeAlias = Generator[Validator, None, None]

Factory: TypeAlias = Callable[..., T]
PyObjectIdFactory: TypeAlias = Factory[PyObjectId]

NoArgsFactory: TypeAlias = Callable[[], T]
NoArgsPyObjectIdFactory: TypeAlias = NoArgsFactory[PyObjectId]

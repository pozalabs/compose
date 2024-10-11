from collections.abc import Callable, Generator
from typing import Any, Self

from .types import PyObjectId

type Validator = Callable[[Any], Self]
type ValidatorGenerator = Generator[Validator, None, None]

type Factory[T] = Callable[..., T]
type PyObjectIdFactory = Factory[PyObjectId]

type NoArgsFactory[T] = Callable[[], T]
type NoArgsPyObjectIdFactory = NoArgsFactory[PyObjectId]

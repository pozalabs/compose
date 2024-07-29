from collections.abc import Callable, Generator
from typing import Any, Self, TypeAlias, TypeVar

T = TypeVar("T")

Validator: TypeAlias = Callable[[Any], Self]
ValidatorGenerator: TypeAlias = Generator[Validator, None, None]

IdFactory: TypeAlias = Callable[..., T]

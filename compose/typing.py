from collections.abc import Callable, Generator
from typing import Any, Self, TypeAlias

Validator: TypeAlias = Callable[[Any], Self]
ValidatorGenerator: TypeAlias = Generator[Validator, None, None]

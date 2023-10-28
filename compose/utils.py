from collections.abc import Generator
from typing import TypeVar

T = TypeVar("T")


def descendants_of(cls: type[T]) -> Generator[T, None, None]:
    stack = cls.__subclasses__()
    while stack:
        current_cls = stack.pop()
        yield current_cls
        stack.extend(current_cls.__subclasses__())

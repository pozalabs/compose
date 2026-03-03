import functools
import os
import sys
import time
import uuid
from collections.abc import Callable, Generator
from typing import Any, get_type_hints


def descendants_of[T](cls: type[T]) -> Generator[type[T], None, None]:
    stack = cls.__subclasses__()
    while stack:
        current_cls = stack.pop()
        yield current_cls
        stack.extend(current_cls.__subclasses__())


def unordered_partial[RT, T](p: functools.partial[RT], t: T) -> Callable[..., RT]:
    type_hints = get_type_hints(p.func)

    exclude_keys = {*p.keywords, "return"}
    candidates = [k for k, v in type_hints.items() if v == t and k not in exclude_keys]

    if len(candidates) != 1:
        raise TypeError(
            f"Cannot inject argument of type {t} into {p}. "
            f"Expected exactly one argument of type {t}, "
            f"but found {len(candidates)}: {candidates}"
        )

    arg_name = candidates[0]

    def wrapper(arg: Any) -> RT:
        return p(**{arg_name: arg})

    return wrapper


def uuid4_hex() -> str:
    return uuid.uuid4().hex


if sys.version_info >= (3, 14):

    def uuid7() -> uuid.UUID:
        return uuid.uuid7()

else:

    def uuid7() -> uuid.UUID:
        timestamp_ms = int(time.time() * 1000)
        rand = int.from_bytes(os.urandom(10))
        value = (timestamp_ms & 0xFFFF_FFFF_FFFF) << 80 | rand
        value = (value & ~(0xF << 76)) | (0x7 << 76)
        value = (value & ~(0x3 << 62)) | (0x2 << 62)
        return uuid.UUID(int=value)


def uuid7_str() -> str:
    return str(uuid7())

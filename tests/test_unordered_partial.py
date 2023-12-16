import functools
from collections.abc import Callable
from typing import TypeVar

import pytest

from compose.utils import unordered_partial

T = TypeVar("T")


class Adder:
    def __init__(self, initial: str):
        self.initial = initial

    def add(self, a: str) -> str:
        return self.initial + a


def add(a: str, adder: Adder) -> str:
    return adder.add(a)


def concat_str(a: str, b: str, c: str) -> str:
    return a + b + c


def test_can_inject_unordered_arg():
    p = functools.partial(add, a=" world")

    assert unordered_partial(p=p, t=Adder)(Adder("hello")) == "hello world"


@pytest.mark.parametrize(
    "unordered_partial_factory, expected_exc_cls, expected_message",
    [
        (
            lambda: unordered_partial(p=functools.partial(concat_str, a="hello"), t=str),
            TypeError,
            f"2: {['b', 'c']}",
        ),
        (
            lambda: unordered_partial(p=functools.partial(add, a="hello"), t=str),
            TypeError,
            f"0: {[]}",
        ),
    ],
    ids=(
        "동일한 타입 인자가 여러 개이면 에러를 일으킨다.",
        "입력 타입과 일치하는 인자가 없으면 에러를 일으킨다.",
    ),
)
def test_cannot_inject_arg(
    unordered_partial_factory: Callable[[], functools.partial[T]],
    expected_exc_cls: type[Exception],
    expected_message: str,
):
    with pytest.raises(expected_exc_cls) as exc_info:
        unordered_partial_factory()

    assert expected_message in str(exc_info.value)

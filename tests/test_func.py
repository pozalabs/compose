from collections.abc import Iterator

import pytest

import compose


@pytest.mark.parametrize(
    "iterator, expected",
    [
        ((i for i in [1, 2, 3] if i == 1), 1),
        ((i for i in [1, 2, 3] if i == 4), None),
        ((i for i in [1, 2, 3] if i == 1), 1),
        ((i for i in [1, 2, 3] if i == 4), None),
    ],
    ids=(
        "일치하는 값을 리턴할 수 있는 제너레이터",
        "일치하는 값을 리턴할 수 없는 제너레이터",
        "일치하는 값을 리턴할 수 있는 리스트 컴프리헨션",
        "일치하는 값을 리턴할 수 없는 리스트 컴프리헨션",
    ),
)
def test_find[T](iterator: Iterator[T], expected: T | None):
    assert compose.func.find(iterator) == expected


@pytest.mark.parametrize(
    "v, expected",
    [(1, 1)],
)
def test_can_unwrap[T](v: T | None, expected: T):
    assert compose.func.unwrap(v, ValueError("Unexpected value")) == expected


@pytest.mark.parametrize(
    "v, exc",
    [
        (None, ValueError("Unexpected value")),
    ],
)
def test_cannot_unwrap[T](v: T | None, exc: Exception):
    with pytest.raises(type(exc)) as exc_info:
        compose.func.unwrap(v, exc)

    assert exc is exc_info.value

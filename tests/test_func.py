from collections.abc import Iterable

import pytest

import compose


@pytest.mark.parametrize(
    "iterable, expected",
    [
        ((i for i in [1, 2, 3] if i == 1), 1),
        ((i for i in [1, 2, 3] if i == 4), None),
        ((i for i in [1, 2, 3] if i == 1), 1),
        ((i for i in [1, 2, 3] if i == 4), None),
        ([1, 2, 3], 1),
        ([], None),
    ],
    ids=(
        "일치하는 값을 리턴할 수 있는 제너레이터",
        "일치하는 값을 리턴할 수 없는 제너레이터",
        "일치하는 값을 리턴할 수 있는 리스트 컴프리헨션",
        "일치하는 값을 리턴할 수 없는 리스트 컴프리헨션",
        "일치하는 값을 리턴할 수 있는 리스트",
        "일치하는 값을 리턴할 수 없는 리스트",
    ),
)
def test_some_or_none[T](iterable: Iterable[T], expected: T | None):
    assert compose.func.some_or_none(iterable) == expected

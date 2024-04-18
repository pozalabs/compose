import io
from typing import IO, TypeVar

import pytest

from compose.stream import chunk_reader

T = TypeVar("T")


@pytest.mark.parametrize(
    "f, chunk_size, expected",
    [
        (io.StringIO("abc"), 1, ["a", "b", "c"]),
        (io.StringIO("abc"), 2, ["ab", "c"]),
        (io.StringIO("abc"), 3, ["abc"]),
    ],
)
def test_chunk_reader(f: IO[T], chunk_size: int, expected: list[T]):
    assert list(chunk_reader(f=f, chunk_size=chunk_size)) == expected

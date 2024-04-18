from collections.abc import Generator
from typing import IO, TypeVar

T = TypeVar("T")


def chunk_reader(f: IO[T], chunk_size: int = 1024 * 1024) -> Generator[T, None, None]:
    while chunk := f.read(chunk_size):
        yield chunk

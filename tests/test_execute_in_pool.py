import concurrent.futures

from compose.concurrent import execute_in_pool


def add(a: int, b: int) -> int:
    return a + b


def test_execute_in_pool():
    funcs = {
        "add_1+2": lambda: add(1, 2),
        "add_3+4": lambda: add(3, 4),
        "add_5+6": lambda: add(5, 6),
    }

    result = execute_in_pool(
        funcs=funcs,
        pool_factory=lambda: concurrent.futures.ThreadPoolExecutor(max_workers=4),
    )

    expected = {
        "add_1+2": 3,
        "add_3+4": 7,
        "add_5+6": 11,
    }

    assert result == expected

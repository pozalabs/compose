import concurrent.futures
import functools

from compose.concurrent import execute_in_pool


def add(a: int, b: int) -> int:
    return a + b


def failing() -> int:
    raise ValueError("pool job failed")


def test_execute_in_pool():
    funcs = {
        "add_1+2": functools.partial(add, 1, 2),
        "add_3+4": functools.partial(add, 3, 4),
        "add_5+6": functools.partial(add, 5, 6),
    }

    result = execute_in_pool(
        pool_factory=lambda: concurrent.futures.ThreadPoolExecutor(max_workers=4),
        funcs=funcs,
    )

    expected = {
        "add_1+2": 3,
        "add_3+4": 7,
        "add_5+6": 11,
    }

    assert result == expected


def test_capture_job_error_with_successful_result():
    funcs = {
        "success": functools.partial(add, 1, 2),
        "failure": functools.partial(failing),
    }

    result = execute_in_pool(
        pool_factory=lambda: concurrent.futures.ThreadPoolExecutor(max_workers=4),
        funcs=funcs,
    )

    assert result["success"] == 3
    assert isinstance(result["failure"], ValueError)
    assert str(result["failure"]) == "pool job failed"

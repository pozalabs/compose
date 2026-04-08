import compose


def add(a: int, b: int) -> int:
    return a + b


def failing() -> int:
    raise ValueError("job failed")


def test_execute():
    executor = compose.concurrent.ThreadPoolExecutor(max_workers=2)
    actual = executor.execute(
        [
            compose.concurrent.ThreadPoolJob(
                f"key-{i}",
                func=add,
                a=i,
                b=i + 1,
            )
            for i in range(2)
        ],
    )

    expected = {"key-0": 1, "key-1": 3}

    assert actual == expected


def test_capture_job_error_with_successful_result():
    executor = compose.concurrent.ThreadPoolExecutor(max_workers=2)

    actual = executor.execute(
        [
            compose.concurrent.ThreadPoolJob("success", func=add, a=1, b=2),
            compose.concurrent.ThreadPoolJob("failure", func=failing),
        ],
    )

    assert actual["success"] == 3
    assert isinstance(actual["failure"], ValueError)
    assert str(actual["failure"]) == "job failed"

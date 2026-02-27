import compose


def add(a: int, b: int) -> int:
    return a + b


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

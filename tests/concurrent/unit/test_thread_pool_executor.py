import compose


def add(a: int, b: int) -> int:
    return a + b


def test_execute_without_group():
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
        group=False,
    )

    expected = [
        compose.concurrent.Result(key="key-0", value=1),
        compose.concurrent.Result(key="key-1", value=3),
    ]

    assert sorted(actual, key=lambda x: x.key) == expected


def test_execute_with_group():
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
        group=True,
    )

    expected = {
        "key-0": compose.concurrent.Result(key="key-0", value=1),
        "key-1": compose.concurrent.Result(key="key-1", value=3),
    }

    assert actual == expected

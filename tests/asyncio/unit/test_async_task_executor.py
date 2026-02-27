import asyncio

import pytest

import compose


async def add_async(a: int, b: int) -> int:
    await asyncio.sleep(0.01)
    return a + b


async def failing_task() -> int:
    await asyncio.sleep(0.01)
    raise ValueError("Task failed")


async def slow_task(delay: float = 0.1) -> str:
    await asyncio.sleep(delay)
    return "completed"


@pytest.mark.asyncio
async def test_execute():
    executor = compose.asyncio.AsyncTaskExecutor(concurrency=2)
    actual = await executor.execute(
        [
            compose.asyncio.AsyncJob(
                f"task-{i}",
                func=add_async,
                a=i,
                b=i + 1,
            )
            for i in range(2)
        ],
    )

    expected = {"task-0": 1, "task-1": 3}

    assert actual == expected


@pytest.mark.asyncio
async def test_execute_with_concurrency_limit():
    executor = compose.asyncio.AsyncTaskExecutor(concurrency=1)

    start_time = asyncio.get_event_loop().time()

    await executor.execute(
        jobs=[
            compose.asyncio.AsyncJob(key=f"task-{i}", func=slow_task, delay=0.05) for i in range(3)
        ],
    )

    end_time = asyncio.get_event_loop().time()
    elapsed = end_time - start_time

    assert elapsed >= 0.15


@pytest.mark.asyncio
async def test_execute_fail_fast():
    executor = compose.asyncio.AsyncTaskExecutor(concurrency=2)

    with pytest.raises(ValueError, match="Task failed"):
        await executor.execute(
            jobs=[
                compose.asyncio.AsyncJob(key="success", func=slow_task, delay=0.1),
                compose.asyncio.AsyncJob(key="failure", func=failing_task),
                compose.asyncio.AsyncJob(key="slow", func=slow_task, delay=0.2),
            ],
        )


@pytest.mark.asyncio
async def test_execute_with_timeout():
    executor = compose.asyncio.AsyncTaskExecutor(concurrency=2, timeout=0.05)

    with pytest.raises(asyncio.TimeoutError):
        await executor.execute(
            jobs=[
                compose.asyncio.AsyncJob(key=f"task-{i}", func=slow_task, delay=0.1)
                for i in range(2)
            ],
        )


@pytest.mark.asyncio
async def test_execute_with_override_timeout():
    executor = compose.asyncio.AsyncTaskExecutor(concurrency=2, timeout=0.01)

    actual = await executor.execute(
        jobs=[
            compose.asyncio.AsyncJob(key=f"task-{i}", func=slow_task, delay=0.02) for i in range(2)
        ],
        timeout=1,
    )

    assert len(actual) == 2
    assert all(value == "completed" for value in actual.values())


@pytest.mark.asyncio
async def test_execute_with_override_concurrency():
    executor = compose.asyncio.AsyncTaskExecutor(concurrency=1)

    start_time = asyncio.get_event_loop().time()

    await executor.execute(
        jobs=[compose.asyncio.AsyncJob(f"task-{i}", slow_task, 0.05) for i in range(3)],
        concurrency=3,
    )

    end_time = asyncio.get_event_loop().time()
    elapsed = end_time - start_time

    assert elapsed < 0.1


@pytest.mark.asyncio
async def test_single_job():
    executor = compose.asyncio.AsyncTaskExecutor(concurrency=2)

    actual = await executor.execute(
        jobs=[compose.asyncio.AsyncJob("task-0", add_async, a=5, b=3)],
    )

    expected = {"task-0": 8}

    assert actual == expected


@pytest.mark.asyncio
async def test_no_timeout():
    executor = compose.asyncio.AsyncTaskExecutor(concurrency=2, timeout=None)

    actual = await executor.execute(
        jobs=[compose.asyncio.AsyncJob(key="task-0", func=slow_task, delay=0.02)],
    )

    assert actual == {"task-0": "completed"}

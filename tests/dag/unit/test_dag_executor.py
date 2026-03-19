import pytest

import compose


def add(a: int, b: int) -> int:
    return a + b


def multiply(a: int, b: int) -> int:
    return a * b


def failing_task(message: str) -> str:
    raise ValueError(f"Task failed: {message}")


def test_execute_no_dependencies():
    executor = compose.dag.DAGExecutor(max_workers=2)

    jobs = [
        compose.dag.DAGJob(
            key="job1",
            dependencies=set(),
            func=add,
            a=1,
            b=2,
        ),
        compose.dag.DAGJob(
            key="job2",
            dependencies=set(),
            func=multiply,
            a=3,
            b=4,
        ),
    ]

    actual = executor.execute(jobs)

    expected = {
        "job1": 3,
        "job2": 12,
    }

    assert actual == expected


def test_execute_with_dependencies():
    """Test execution of jobs with dependencies"""
    executor = compose.dag.DAGExecutor(max_workers=2)

    jobs = [
        compose.dag.DAGJob(
            key="stage1_a",
            dependencies=set(),
            func=add,
            a=1,
            b=2,
        ),
        compose.dag.DAGJob(
            key="stage1_b",
            dependencies=set(),
            func=add,
            a=3,
            b=4,
        ),
        compose.dag.DAGJob(
            key="stage2",
            dependencies={"stage1_a", "stage1_b"},
            func=multiply,
            a=2,
            b=3,
        ),
    ]

    actual = executor.execute(jobs)

    expected = {
        "stage1_a": 3,
        "stage1_b": 7,
        "stage2": 6,
    }

    assert actual == expected


def test_execute_diamond_dependency():
    executor = compose.dag.DAGExecutor(max_workers=2)

    jobs = [
        compose.dag.DAGJob(
            key="root",
            dependencies=set(),
            func=add,
            a=10,
            b=5,
        ),
        compose.dag.DAGJob(
            key="left_branch",
            dependencies={"root"},
            func=multiply,
            a=2,
            b=3,
        ),
        compose.dag.DAGJob(
            key="right_branch",
            dependencies={"root"},
            func=add,
            a=1,
            b=1,
        ),
        compose.dag.DAGJob(
            key="convergence",
            dependencies={"left_branch", "right_branch"},
            func=add,
            a=100,
            b=200,
        ),
    ]

    actual = executor.execute(jobs)

    expected = {
        "root": 15,
        "left_branch": 6,
        "right_branch": 2,
        "convergence": 300,
    }

    assert actual == expected


def test_execute_empty_jobs():
    executor = compose.dag.DAGExecutor(max_workers=2)

    actual = executor.execute([])

    assert actual == {}


def test_execute_with_exception():
    executor = compose.dag.DAGExecutor(max_workers=2)

    jobs = [
        compose.dag.DAGJob(
            key="normal",
            dependencies=set(),
            func=add,
            a=1,
            b=2,
        ),
        compose.dag.DAGJob(
            key="failing",
            dependencies=set(),
            func=failing_task,
            message="test error",
        ),
    ]

    with pytest.raises(ValueError, match="Task failed: test error"):
        executor.execute(jobs)

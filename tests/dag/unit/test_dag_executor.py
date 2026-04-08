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
        compose.dag.DAGJob.fixed(
            key="job1",
            func=add,
            a=1,
            b=2,
        ),
        compose.dag.DAGJob.fixed(
            key="job2",
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
    executor = compose.dag.DAGExecutor(max_workers=2)

    jobs = [
        compose.dag.DAGJob.fixed(
            key="stage1_a",
            func=add,
            a=1,
            b=2,
        ),
        compose.dag.DAGJob.fixed(
            key="stage1_b",
            func=add,
            a=3,
            b=4,
        ),
        compose.dag.DAGJob.fixed(
            key="stage2",
            func=multiply,
            a=2,
            b=3,
            dependencies={"stage1_a", "stage1_b"},
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
        compose.dag.DAGJob.fixed(
            key="root",
            func=add,
            a=10,
            b=5,
        ),
        compose.dag.DAGJob.fixed(
            key="left_branch",
            func=multiply,
            a=2,
            b=3,
            dependencies={"root"},
        ),
        compose.dag.DAGJob.fixed(
            key="right_branch",
            func=add,
            a=1,
            b=1,
            dependencies={"root"},
        ),
        compose.dag.DAGJob.fixed(
            key="convergence",
            func=add,
            a=100,
            b=200,
            dependencies={"left_branch", "right_branch"},
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
        compose.dag.DAGJob.fixed(
            key="normal",
            func=add,
            a=1,
            b=2,
        ),
        compose.dag.DAGJob.fixed(
            key="failing",
            func=failing_task,
            message="test error",
        ),
    ]

    with pytest.raises(ValueError, match="Task failed: test error"):
        executor.execute(jobs)


def test_inject_dependency_result_into_downstream_job():
    executor = compose.dag.DAGExecutor(max_workers=2)

    jobs = [
        compose.dag.DAGJob.fixed(
            key="fetch",
            func=add,
            a=10,
            b=5,
        ),
        compose.dag.DAGJob(
            key="process",
            dependencies={"fetch"},
            func=lambda results: results["fetch"] * 3,
        ),
    ]

    actual = executor.execute(jobs)

    assert actual == {"fetch": 15, "process": 45}


def test_inject_multiple_dependency_results():
    executor = compose.dag.DAGExecutor(max_workers=2)

    jobs = [
        compose.dag.DAGJob.fixed(key="a", func=add, a=1, b=2),
        compose.dag.DAGJob.fixed(key="b", func=add, a=3, b=4),
        compose.dag.DAGJob(
            key="sum",
            dependencies={"a", "b"},
            func=lambda results: results["a"] + results["b"],
        ),
    ]

    actual = executor.execute(jobs)

    assert actual == {"a": 3, "b": 7, "sum": 10}


def test_results_contain_only_declared_dependencies():
    executor = compose.dag.DAGExecutor(max_workers=1)
    received_keys: set[str] = set()

    def capture_keys(results: dict) -> int:
        received_keys.update(results.keys())
        return results["a"] + 1

    jobs = [
        compose.dag.DAGJob.fixed(key="a", func=add, a=1, b=2),
        compose.dag.DAGJob.fixed(key="unrelated", func=add, a=10, b=20),
        compose.dag.DAGJob(
            key="downstream",
            dependencies={"a"},
            func=capture_keys,
        ),
    ]

    executor.execute(jobs)

    assert received_keys == {"a"}


def test_fixed_ignore_dependency_results():
    executor = compose.dag.DAGExecutor(max_workers=1)

    jobs = [
        compose.dag.DAGJob.fixed(key="upstream", func=add, a=1, b=2),
        compose.dag.DAGJob.fixed(
            key="downstream",
            func=multiply,
            a=5,
            b=6,
            dependencies={"upstream"},
        ),
    ]

    actual = executor.execute(jobs)

    assert actual == {"upstream": 3, "downstream": 30}

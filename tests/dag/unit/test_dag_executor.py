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
        compose.dag.DAGJob.bound("job1", add, a=1, b=2),
        compose.dag.DAGJob.bound("job2", multiply, a=3, b=4),
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
        compose.dag.DAGJob.bound("stage1_a", add, a=1, b=2),
        compose.dag.DAGJob.bound("stage1_b", add, a=3, b=4),
        compose.dag.DAGJob(
            key="stage2",
            dependencies={"stage1_a", "stage1_b"},
            func=lambda _: multiply(a=2, b=3),
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
        compose.dag.DAGJob.bound("root", add, a=10, b=5),
        compose.dag.DAGJob(
            key="left_branch",
            dependencies={"root"},
            func=lambda _: multiply(a=2, b=3),
        ),
        compose.dag.DAGJob(
            key="right_branch",
            dependencies={"root"},
            func=lambda _: add(a=1, b=1),
        ),
        compose.dag.DAGJob(
            key="convergence",
            dependencies={"left_branch", "right_branch"},
            func=lambda _: add(a=100, b=200),
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
        compose.dag.DAGJob.bound("normal", add, a=1, b=2),
        compose.dag.DAGJob.bound("failing", failing_task, message="test error"),
    ]

    with pytest.raises(ValueError, match="Task failed: test error"):
        executor.execute(jobs)


def test_inject_dependency_result_into_downstream_job():
    executor = compose.dag.DAGExecutor(max_workers=2)

    jobs = [
        compose.dag.DAGJob.bound("fetch", add, a=10, b=5),
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
        compose.dag.DAGJob.bound("a", add, a=1, b=2),
        compose.dag.DAGJob.bound("b", add, a=3, b=4),
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
        compose.dag.DAGJob.bound("a", add, a=1, b=2),
        compose.dag.DAGJob.bound("unrelated", add, a=10, b=20),
        compose.dag.DAGJob(
            key="downstream",
            dependencies={"a"},
            func=capture_keys,
        ),
    ]

    executor.execute(jobs)

    assert received_keys == {"a"}


def test_bound_job_ignore_dependency_results():
    executor = compose.dag.DAGExecutor(max_workers=1)

    jobs = [
        compose.dag.DAGJob.bound("upstream", add, a=1, b=2),
        compose.dag.DAGJob(
            key="downstream",
            dependencies={"upstream"},
            func=lambda _: multiply(a=5, b=6),
        ),
    ]

    actual = executor.execute(jobs)

    assert actual == {"upstream": 3, "downstream": 30}

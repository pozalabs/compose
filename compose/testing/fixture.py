from typing import Any

try:
    import pytest
except ImportError:
    raise ImportError(
        "`pytest` is required to use testing package. "
        "Install compose with `pytest` extra, `compose[pytest]`."
    )


def get_fixture(request: pytest.FixtureRequest) -> Any:
    fixture_name: str = request.param
    return request.getfixturevalue(fixture_name)

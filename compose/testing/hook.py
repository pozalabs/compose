from collections.abc import Callable
from pathlib import Path

import pytest

from compose.enums import AppEnv

from .enums import TestTypeMarker

MARKER_NAME_TO_MARKER = {
    marker_name: getattr(pytest.mark, marker_name) for marker_name in TestTypeMarker.names()
}


def check_env_is_allowed(env: AppEnv | None) -> None:
    if env is None or env != AppEnv.TEST:
        raise RuntimeError(f"`APP_ENV` must be set to `{AppEnv.TEST}` to run tests")


def register_test_type_markers(config: pytest.Config) -> None:
    for member in TestTypeMarker:
        name, description = member.value
        config.addinivalue_line("markers", f"{name}: {description}")


def default_marker_getter(item: pytest.Function) -> pytest.MarkDecorator:
    test_types = set(MARKER_NAME_TO_MARKER.keys())
    default_test_type = pytest.mark.unit.name

    node_path = item.nodeid.split("::")[0]
    parts = Path(node_path).parts
    return next((part for part in parts if part in test_types), default_test_type)


def add_test_type_markers(
    items: list[pytest.Function],
    marker_getter: Callable[[pytest.Function], pytest.MarkDecorator] = default_marker_getter,
) -> None:
    """

    Examples:
        >>> from compose import testing
        >>> import pytest
        >>> def pytest_collection_modifyitems(items: list[pytest.Function]) -> None:
        >>>     testing.add_test_type_markers(items)

    """

    for item in items:
        item.add_marker(marker_getter(item))

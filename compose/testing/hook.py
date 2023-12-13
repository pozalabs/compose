from collections.abc import Callable
from pathlib import Path

import pytest


def default_marker_getter(item: pytest.Function) -> pytest.MarkDecorator:
    test_type_to_marker = {
        marker.name: marker
        for marker in [pytest.mark.unit, pytest.mark.integration, pytest.mark.e2e]
    }
    test_types = set(test_type_to_marker.keys())
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

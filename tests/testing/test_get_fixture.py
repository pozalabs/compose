import pytest

from compose.testing.fixture import get_fixture


@pytest.fixture
def tst_fixture1() -> int:
    return 1


@pytest.fixture
def tst_fixture2() -> int:
    return 2


@pytest.fixture
def tst_fixture(request: pytest.FixtureRequest) -> int:
    return get_fixture(request)


@pytest.mark.parametrize(
    "tst_fixture, expected",
    [
        ("tst_fixture1", 1),
        ("tst_fixture2", 2),
    ],
    indirect=["tst_fixture"],
)
def test_get_fixture(tst_fixture: int, expected: int):
    assert tst_fixture == expected

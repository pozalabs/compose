import pytest

import compose


@pytest.mark.parametrize(
    "mib, expected",
    [
        (1, 1048576),
        (10, 10485760),
    ],
)
def test_from_mib(mib: int, expected: compose.types.Byte):
    assert compose.types.Byte.from_mib(mib) == expected


@pytest.mark.parametrize(
    "gib, expected",
    [
        (1, 1073741824),
        (10, 10737418240),
    ],
)
def test_from_gib(gib: float, expected: compose.types.Byte):
    assert compose.types.Byte.from_gib(gib) == expected

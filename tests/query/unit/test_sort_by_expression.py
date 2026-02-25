import pytest

from compose.query.mongo.op import SortBy


def test_asc_expression():
    assert SortBy.asc("field").expression() == {"field": 1}


def test_desc_expression():
    assert SortBy.desc("field").expression() == {"field": -1}


@pytest.mark.parametrize(
    "key, expected",
    [
        ("field", {"field": 1}),
        ("-field", {"field": -1}),
    ],
    ids=(
        "정렬 키에 접두사가 없으면 오름차순을 적용한다.",
        "정렬 키에 `-` 접두사가 있으면 내림차순을 적용한다.",
    ),
)
def test_parse_expression(key: str, expected: dict[str, int]):
    assert SortBy.parse(key).expression() == expected

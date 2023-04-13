import pytest

from compose.query.mongo.op import AggVar


@pytest.mark.parametrize(
    "value, expected",
    [
        (AggVar("$field"), "$field"),
        (AggVar("$$field"), "$$field"),
        (AggVar("field"), "$$field"),
    ],
    ids=(
        "`AggVar`는 입력값이 `$` 한개로 시작하면 입력값을 그대로 사용한다.",
        "`AggVar`는 입력값이  `$` 두개로 시작하면 입력값을 그대로 사용한다.",
        "`AggVar`는 입력값이 `$`로 시작하지 않으면 `$` 두개를 입력값에 접두사로 추가한다.",
    ),
)
def test_initiate(value: str, expected: str):
    assert value == expected


def test_cannot_initiate_agg_var():
    with pytest.raises(ValueError):
        AggVar("$$$field")

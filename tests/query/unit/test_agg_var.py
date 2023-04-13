import pytest

from compose.query.mongo.op import AggVar


@pytest.mark.parametrize(
    "value, expected",
    [
        (AggVar("$field"), "$field"),
        (AggVar("$$field"), "$$field"),
    ],
    ids=(
        "`AggVar`는 입력값이 `$` 한개로 시작하면 입력값을 그대로 사용한다.",
        "`AggVar`는 입력값이  `$` 두개로 시작하면 입력값을 그대로 사용한다.",
    ),
)
def test_initiate(value: str, expected: str):
    assert value == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("field", "$$field"),
    ],
    ids=("`AggVar.from_`은 문자열을 Aggregation Variable로 변환한다.",),
)
def test_from(value: str, expected: str):
    assert AggVar.from_(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "field",
        "$$$field",
    ],
    ids=(
        "`AggVar`는 `$`로 시작하지 않는 입력값은 올바르지 않은 값으로 판단하다.",
        "`AggVar`는 세개 이상의 `$`로 시작하는 입력값은 올바르지 않은 값으로 판단한다",
    ),
)
def test_cannot_initiate_agg_var(value: str):
    with pytest.raises(ValueError):
        AggVar(value)

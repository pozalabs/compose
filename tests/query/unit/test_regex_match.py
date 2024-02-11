import pytest

from compose.query.mongo.op import DictExpression, RegexMatch, ToString


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            RegexMatch(field="field", value="value"),
            {"$regexMatch": {"input": "field", "regex": "value"}},
        ),
        (
            RegexMatch(field=ToString(10), value="value"),
            {"$regexMatch": {"input": {"$toString": 10}, "regex": "value"}},
        ),
    ],
    ids=(
        "문자열 필드를 사용하는 경우",
        "표현식 필드를 사용하는 경우",
    ),
)
def test_expression(op: RegexMatch, expected: DictExpression):
    assert op.expression() == expected

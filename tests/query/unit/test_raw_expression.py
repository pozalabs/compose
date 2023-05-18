import pytest

from compose.query.mongo.op import Expression, Raw


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            Raw({"$match": {"field": "value"}}),
            {"$match": {"field": "value"}},
        ),
        (
            Raw([{"$match": {"field": "value"}}]),
            [{"$match": {"field": "value"}}],
        ),
    ],
    ids=(
        "입력한 표현식이 `DictExpression`이면 `DictExpression`을 리턴한다.",
        "입력한 표현식이 `ListExpression`이면 `ListExpression`을 리턴한다.",
    ),
)
def test_expression(op: Raw, expected: Expression):
    assert op.expression() == expected

import pytest

from compose.query.mongo.op import DictExpression, Raw, ReplaceRoot


@pytest.mark.parametrize(
    "op, expected",
    [
        (ReplaceRoot("$field"), {"$replaceRoot": {"newRoot": "$field"}}),
        (
            ReplaceRoot({"$mergeObjects": ["$root", "$$ROOT"]}),
            {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$root", "$$ROOT"]}}},
        ),
        (
            ReplaceRoot(Raw({"$mergeObjects": ["$root", "$$ROOT"]})),
            {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$root", "$$ROOT"]}}},
        ),
    ],
    ids=(
        "필드를 입력하는 경우",
        "표현식 객체를 입력하는 경우",
        "`Operator`를 입력하면 생성된 표현식을 사용한다.",
    ),
)
def test_expression(op: ReplaceRoot, expected: DictExpression):
    assert op.expression() == expected

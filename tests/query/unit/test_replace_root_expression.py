from typing import Any

import pytest

from compose.query.mongo.op import DictExpression, Raw, ReplaceRoot


@pytest.mark.parametrize(
    "new_root, expected",
    [
        ("$field", {"$replaceRoot": {"newRoot": "$field"}}),
        (
            {"$mergeObjects": ["$root", "$$ROOT"]},
            {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$root", "$$ROOT"]}}},
        ),
        (
            Raw({"$mergeObjects": ["$root", "$$ROOT"]}),
            {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$root", "$$ROOT"]}}},
        ),
    ],
    ids=(
        "필드를 입력하는 경우",
        "표현식 객체를 입력하는 경우",
        "`Operator`를 입력하면 생성된 표현식을 사용한다.",
    ),
)
def test_expression(new_root: Any, expected: DictExpression):
    assert ReplaceRoot(new_root).expression() == expected

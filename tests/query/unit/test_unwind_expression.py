import pytest

from compose.query.mongo.op import DictExpression, Unwind


@pytest.mark.parametrize(
    "op, expected",
    [
        (Unwind("$field"), {"$unwind": {"path": "$field"}}),
        (
            Unwind(path="$field", include_array_index="idx", preserve_null_and_empty_arrays=True),
            {
                "$unwind": {
                    "path": "$field",
                    "includeArrayIndex": "idx",
                    "preserveNullAndEmptyArrays": True,
                }
            },
        ),
        (
            Unwind.preserve_missing(path="$field"),
            {"$unwind": {"path": "$field", "preserveNullAndEmptyArrays": True}},
        ),
    ],
    ids=(
        "선택 옵션을 입력하지 않으면 입력된 키/값으로만 표현식이 구성된다.",
        "선택 옵션을 입력하면 선택 옵션이 포함되어 표현식이 구성된다.",
        "`preserve_missing` 메서드를 사용하면 `preserveNullAndEmptyArrays`를 `True`로 설정한다.",
    ),
)
def test_expression(op: Unwind, expected: DictExpression):
    assert op.expression() == expected

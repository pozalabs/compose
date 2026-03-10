from typing import Any

import pytest

from compose.query.mongo.op import AEq, Filter, Raw, Spec
from compose.query.mongo.op.base import deep_evaluate


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            Spec(field="field", spec=1),
            {"field": 1},
        ),
        (
            {"field": 1},
            {"field": 1},
        ),
        (
            "$field",
            "$field",
        ),
        (
            {
                "$mergeObjects": [
                    "$$tag",
                    Spec(
                        field="keyword",
                        spec=Raw(
                            {
                                "$first": Filter(
                                    input_="$keywords",
                                    as_="keyword",
                                    cond=AEq("$$keyword._id", "$$tag.keyword_id"),
                                )
                            }
                        ),
                    ),
                ]
            },
            {
                "$mergeObjects": [
                    "$$tag",
                    {
                        "keyword": {
                            "$first": {
                                "$filter": {
                                    "input": "$keywords",
                                    "as": "keyword",
                                    "cond": {"$eq": ["$$keyword._id", "$$tag.keyword_id"]},
                                }
                            }
                        }
                    },
                ]
            },
        ),
    ],
    ids=(
        "`Operator`를 입력하면 평가한 표현식을 리턴한다.",
        "딕셔너리를 입력하면 값을 그대로 리턴한다",
        "문자열을 입력하면 값을 그대로 리턴한다",
        "원시 표현식과 `Operator`로 이루어진 중첩 평가식을 중첩문 가장 아래까지 모두 평가한다.",
    ),
)
def test_deep_evaluate(value: Any, expected: Any):
    assert deep_evaluate(value) == expected

from typing import Any

import pytest

from compose.query.mongo.op import Specification
from compose.query.mongo.op.types import Input


@pytest.mark.parametrize(
    "input_value, expected",
    [(1, 1), (Specification(field="field", spec="spec"), {"field": "spec"})],
    ids=(
        "입력값이 `Expressionable`이 아니면 입력값을 그대로 리턴한다.",
        "입력값이 `Expressionable`이면 `expression` 메서드의 리턴값을 리턴한다.",
    ),
)
def test_unwrap(input_value: Any, expected: Any) -> None:
    assert Input(input_value).unwrap() == expected

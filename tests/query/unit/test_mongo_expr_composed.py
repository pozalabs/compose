import operator
from typing import Any, Callable, Iterable, Optional

import pytest

from compose.query.mongo.expr import Composed, Empty, Expression


class CustomExpression(Expression):
    def __init__(self, field: str, value: Optional[Any]):
        self.field = field
        self.value = value

    def expression(self) -> dict[str, Any]:
        return {self.field: self.value}


@pytest.mark.parametrize(
    "composer, expressions, expected",
    [
        (operator.and_, [CustomExpression(field="field", value="value")], {"field": "value"}),
        (operator.and_, [Empty.dict(), CustomExpression(field="field", value="value")], {}),
    ],
    ids=(
        "단일 표현식은 해당 표현식을 그대로 리턴",
        "다중 표현식은 `composer`에 표현식을 적용한 결과를 리턴",
    ),
)
def test_composed(
    composer: Callable[[Expression, Expression], Expression],
    expressions: Iterable[Expression],
    expected: dict[str, Any],
):
    composed = Composed(*expressions, composer=composer)

    assert composed.expression() == expected

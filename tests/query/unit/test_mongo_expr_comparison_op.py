from typing import Any, Callable, Type

import pytest

from compose.query.mongo.expr.op import ComparisonOperator, OptionalValue, Value, ValueType


@pytest.fixture
def comparison_operator_cls() -> Type[ComparisonOperator]:
    class Operator(ComparisonOperator):
        def __init__(self, field: str, value: ValueType):
            super().__init__(field=field, value=value)

        def get_expression(self) -> dict[str, Any]:
            return {self.field: self.value}

    return Operator


@pytest.fixture
def comparison_operator_factory(
    comparison_operator_cls: Type[ComparisonOperator],
) -> Callable[..., ComparisonOperator]:
    def _factory(value: ValueType) -> ComparisonOperator:
        return comparison_operator_cls(field="field", value=value)

    return _factory


@pytest.mark.parametrize(
    "value, expected",
    [
        (OptionalValue(None), {}),
        (Value(None), {"field": None}),
        (Value("value"), {"field": "value"}),
    ],
    ids=(
        "비교 대상이 `OptionalValue`로 감싼 None이면 빈 딕셔너리 리턴",
        "비교 대상이 `Value`로 감싼 None이면 None과 비교하는 표현식 리턴",
        "비교 대상이 `Value`로 감싼 값이면 해당 값과 비교하는 표현식 리턴",
    ),
)
def test_comparison_operator(
    comparison_operator_factory: Callable[..., ComparisonOperator],
    value: ValueType,
    expected: dict[str, Any],
):
    op = comparison_operator_factory(value=value)

    assert op.expression() == expected

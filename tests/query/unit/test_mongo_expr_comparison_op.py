from typing import Any, Callable, Type

import pytest

from compose.query.mongo.expr.op import ComparisonOperator, OptionalWrapped, Wrapped, WrappedType


@pytest.fixture
def comparison_operator_cls() -> Type[ComparisonOperator]:
    class Operator(ComparisonOperator):
        def __init__(self, field: str, value: WrappedType):
            super().__init__(field=field, value=value)

        def get_expression(self) -> dict[str, Any]:
            return {self.field: self.value}

    return Operator


@pytest.fixture
def comparison_operator_factory(
    comparison_operator_cls: Type[ComparisonOperator],
) -> Callable[..., ComparisonOperator]:
    def _factory(value: WrappedType) -> ComparisonOperator:
        return comparison_operator_cls(field="field", value=value)

    return _factory


@pytest.mark.parametrize(
    "value, expected",
    [
        (OptionalWrapped(None), {}),
        (Wrapped(None), {"field": None}),
        (Wrapped("value"), {"field": "value"}),
    ],
    ids=(
        "값이 None이고 `OptionalWrapped`이면 빈 딕셔너리 리턴",
        "값이 None이고 `Wrapped`로 감싸면 None과 비교하는 표현식 리턴",
        "값이 None이 아니고 `Wrapped`로 감싸면 해당 값과 비교하는 표현식 리턴",
    ),
)
def test_comparison_operator(
    comparison_operator_factory: Callable[..., ComparisonOperator],
    value: WrappedType,
    expected: dict[str, Any],
):
    op = comparison_operator_factory(value=value)

    assert op.expression() == expected

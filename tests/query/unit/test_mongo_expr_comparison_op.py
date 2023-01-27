from typing import Any, Callable, Optional, Type

import pytest

from compose.query.mongo.expr.op import ComparisonOperator


@pytest.fixture
def comparison_operator_cls() -> Type[ComparisonOperator]:
    class Operator(ComparisonOperator):
        def __init__(self, field: str, value: Optional[str] = None, compare_none: bool = False):
            super().__init__(field=field, value=value, compare_none=compare_none)

        def get_expression(self) -> dict[str, Any]:
            return {self.field: self.value}

    return Operator


@pytest.fixture
def comparison_operator_factory(
    comparison_operator_cls: Type[ComparisonOperator],
) -> Callable[..., ComparisonOperator]:
    def _factory(value: Optional[str], compare_none: bool) -> ComparisonOperator:
        return comparison_operator_cls(field="field", value=value, compare_none=compare_none)

    return _factory


@pytest.mark.parametrize(
    "value, compare_none, expected",
    [
        (None, False, {}),
        (None, True, {"field": None}),
        ("value", True, {"field": "value"}),
    ],
    ids=(
        "값이 None이고 None과 비교하지 않으면 빈 딕셔너리 리턴",
        "값이 None이고 None과 비교하면 None과 비교하는 표현식 리턴",
        "값이 None이 아니면 항상 해당 값과 비교하는 표현식 리턴",
    ),
)
def test_comparison_operator(
    comparison_operator_factory: Callable[..., ComparisonOperator],
    value: Optional[str],
    compare_none: bool,
    expected: dict[str, Any],
):
    op = comparison_operator_factory(value=value, compare_none=compare_none)

    assert op.expression() == expected

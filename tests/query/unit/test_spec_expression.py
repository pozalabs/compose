from collections.abc import Callable

import pytest

from compose.query.mongo.op import DictExpression, Spec


@pytest.mark.parametrize(
    "spec, expected",
    [
        (Spec(field="field", spec="value"), {"field": "value"}),
        (Spec.include("field"), {"field": 1}),
        (Spec.exclude("field"), {"field": 0}),
        (Spec.ref(field="field", spec="$ref"), {"field": "$ref"}),
    ],
    ids=(
        "`field`에 입력한 인자를 할당하는 표현식을 리턴한다.",
        "`include()` 메서드를 사용하면 `field`에 1을 할당하는 표현식을 리턴한다.",
        "`exclude()` 메서드를 사용하면 `field`에 0을 할당하는 표현식을 리턴한다.",
        "`ref()` 메서드를 사용하면 `field`에 `spec`을 할당하는 표현식을 리턴한다.",
    ),
)
def test_expression(spec: Spec, expected: DictExpression):
    assert spec.expression() == expected


@pytest.mark.parametrize(
    "spec_factory, exc_type",
    [
        (
            lambda: Spec.ref(field="field", spec="value"),
            ValueError,
        )
    ],
    ids=("`ref()` 메서드 사용시 `spec` 인자는 `$`로 시작해야 한다.",),
)
def test_cannot_create_spec(
    spec_factory: Callable[[], Spec],
    exc_type: type[Exception],
):
    with pytest.raises(exc_type):
        spec_factory()

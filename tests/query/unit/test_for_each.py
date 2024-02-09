from collections.abc import Callable

import pytest

from compose.query.mongo.op import ForEach, Operator, Spec, Split


@pytest.mark.parametrize(
    "factory, expected",
    [
        (
            lambda: ForEach(
                ["field1", "field2"],
                lambda v: Spec(field=v, spec=Split(expr=v, delimiter=" ")),
            ),
            [
                Spec(field="field1", spec=Split(expr="field1", delimiter=" ")),
                Spec(field="field2", spec=Split(expr="field2", delimiter=" ")),
            ],
        ),
        (
            lambda: ForEach(
                [("field1", "value1"), ("field2", "value2")],
                lambda v: Spec(field=v[0], spec=Split(expr=v[1], delimiter=" ")),
            ),
            [
                Spec(field="field1", spec=Split(expr="value1", delimiter=" ")),
                Spec(field="field2", spec=Split(expr="value2", delimiter=" ")),
            ],
        ),
        (
            lambda: ForEach(
                [dict(key="field1", value="value1"), dict(key="field2", value="value2")],
                lambda v: Spec(field=v["key"], spec=Split(expr=v["value"], delimiter=" ")),
            ),
            [
                Spec(field="field1", spec=Split(expr="value1", delimiter=" ")),
                Spec(field="field2", spec=Split(expr="value2", delimiter=" ")),
            ],
        ),
    ],
    ids=(
        "인자 1개를 사용하는 경우",
        "인자 2개를 사용하는 경우",
        "딕셔너리 인자를 사용하는 경우",
    ),
)
def test_for_each(factory: Callable[[], ForEach], expected: list[Operator]):
    assert [op.expression() for op in factory()] == [op.expression() for op in expected]

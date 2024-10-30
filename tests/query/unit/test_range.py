from typing import Any

import pendulum
import pytest

from compose.query.mongo.op import Range


@pytest.mark.parametrize(
    "op, expected",
    [
        (
            Range.date(
                field="created_at",
                from_=pendulum.datetime(2024, 10, 1),
                to=pendulum.datetime(2024, 10, 2),
            ),
            {
                "created_at": {
                    "$gte": pendulum.datetime(2024, 10, 1),
                    "$lt": pendulum.datetime(2024, 10, 2),
                }
            },
        )
    ],
)
def test_expression(op: Range, expected: dict[str, Any]):
    assert op.expression() == expected

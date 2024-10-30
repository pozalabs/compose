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
                start=pendulum.datetime(2024, 10, 1),
                end=pendulum.datetime(2024, 10, 2),
            ),
            {
                "created_at": {
                    "$gte": pendulum.datetime(2024, 10, 1),
                    "$lt": pendulum.datetime(2024, 10, 2),
                }
            },
        ),
        (
            Range.day(
                field="created_at",
                dt=pendulum.datetime(2024, 10, 2, tz="Asia/Seoul"),
            ),
            {
                "created_at": {
                    "$gte": pendulum.datetime(2024, 10, 1, 15),
                    "$lt": pendulum.datetime(2024, 10, 2, 15),
                }
            },
        ),
    ],
)
def test_expression(op: Range, expected: dict[str, Any]):
    assert op.expression() == expected

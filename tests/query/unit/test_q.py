from typing import Any

import pytest

from compose.query.mongo.op import And, Eq, Operator
from compose.query.mongo.query import q


@pytest.mark.parametrize(
    "ops, expected",
    [
        (
            [
                And(
                    Eq("name", "pozalabs"),
                    Eq("age", 30),
                )
            ],
            {
                "$and": [
                    {"name": {"$eq": "pozalabs"}},
                    {"age": {"$eq": 30}},
                ]
            },
        ),
    ],
)
def test_expression(ops: list[Operator], expected: dict[str, Any]):
    assert q(*ops) == expected

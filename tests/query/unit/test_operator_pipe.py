from typing import Any

import pytest

from compose.query.mongo.op import Filter, Operator, Size, ToBool


@pytest.mark.parametrize(
    "chained_op, expected",
    [
        (
            (
                Filter(
                    input_="$field",
                    as_="output",
                    cond={"$eq": ["$$field", "value"]},
                )
                .pipe(Size)
                .pipe(lambda x: ToBool(x))
            ),
            {
                "$toBool": {
                    "$size": {
                        "$filter": {
                            "input": "$field",
                            "as": "output",
                            "cond": {"$eq": ["$$field", "value"]},
                        }
                    }
                }
            },
        )
    ],
    ids=("Filter -> Size -> ToBool",),
)
def test_pipe(chained_op: Operator, expected: Any):
    assert chained_op.expression() == expected

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
                .fmap(Size)
                .fmap(ToBool)
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
def test_fmap(chained_op: Operator, expected: Any):
    assert chained_op.expression() == expected

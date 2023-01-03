from typing import Union

import bson
import pytest

from compose.types import PyObjectId


@pytest.mark.parametrize(
    "object_id, expected",
    [
        (bson.ObjectId(b"test-id-0001"), PyObjectId(b"test-id-0001")),
        (b"test-id-0002", PyObjectId(b"test-id-0002")),
    ],
    ids=(
        "유효한 bson.ObjectId는 유효한 PyObjectId",
        "유효한 12 bytes는 유효한 PyObjectId",
    ),
)
def test_validate(object_id: Union[bson.ObjectId, bytes], expected: PyObjectId):
    actual = PyObjectId.validate(object_id)

    assert actual == expected

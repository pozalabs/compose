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


@pytest.mark.parametrize(
    "object_id",
    [b"invalid-id", "invalid-id"],
    ids=(
        "12자리가 아닌 bytes는 유효하지 않은 PyObjectId",
        "24자리 hex digit이 아닌 문자열은 유효하지 않은 PyObjectId",
    ),
)
def test_validate_invalid_id(object_id: Union[bytes, str]):
    with pytest.raises(ValueError):
        PyObjectId.validate(object_id)

import bson
import pytest

import compose


@pytest.mark.parametrize(
    "object_id, expected",
    [
        (bson.ObjectId(b"test-id-0001"), compose.types.PyObjectId(b"test-id-0001")),
        (b"test-id-0002", compose.types.PyObjectId(b"test-id-0002")),
    ],
    ids=(
        "유효한 bson.ObjectId는 유효한 PyObjectId",
        "유효한 12 bytes는 유효한 PyObjectId",
    ),
)
def test_validate(object_id: bson.ObjectId | bytes, expected: compose.types.PyObjectId):
    actual = compose.compat.validate_obj(compose.types.PyObjectId, object_id)

    assert actual == expected


@pytest.mark.parametrize(
    "object_id",
    [b"invalid-id", "invalid-id"],
    ids=(
        "12자리가 아닌 bytes는 유효하지 않은 PyObjectId",
        "24자리 hex digit이 아닌 문자열은 유효하지 않은 PyObjectId",
    ),
)
def test_validate_invalid_id(object_id: bytes | str):
    with pytest.raises(ValueError):
        compose.compat.validate_obj(compose.types.PyObjectId, object_id)

import copy
from typing import Any
from unittest import mock

import pytest
from pymongo.collection import Collection

import compose


class Model(compose.entity.Entity):
    name: str


@pytest.fixture
def model_data() -> dict[str, Any]:
    return dict(
        id=compose.types.PyObjectId(b"test-id-0001"),
        name="name01",
        created_at=compose.types.DateTime(2023, 1, 13),
        updated_at=compose.types.DateTime(2023, 1, 13),
    )


@pytest.fixture
def fake_collection(model_data: dict[str, Any]) -> Collection:
    collection = mock.Mock(spec=Collection)
    collection.find_one = mock.Mock(return_value=model_data)
    return collection


@pytest.fixture
def fake_mongo_repository(fake_collection: Collection) -> compose.repository.MongoRepository[Model]:
    class ModelRepository(compose.repository.MongoRepository[Model]):
        __collection_name__ = "model"

    return ModelRepository(fake_collection)


@pytest.fixture
def expected(model_data: dict[str, Any]) -> Model:
    return Model(**copy.deepcopy(model_data))


def test_mongo_repository_find_by_return_concrete_entity_type(
    fake_mongo_repository: compose.repository.MongoRepository[Model],
    expected: Model,
):
    actual = fake_mongo_repository.find_by({"_id": compose.types.PyObjectId(b"test-id-0001")})

    assert actual == expected

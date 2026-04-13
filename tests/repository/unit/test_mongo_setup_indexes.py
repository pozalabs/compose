from unittest import mock

import pymongo
import pytest
from pymongo.collection import Collection

import compose


class Model(compose.entity.MongoEntity):
    name: str


@pytest.fixture
def fake_collection() -> mock.Mock:
    return mock.Mock(spec=Collection)


def test_ensure_indexes_create_registered_indexes_on_collection(fake_collection: mock.Mock):
    indexes = [pymongo.IndexModel([("name", 1)], name="name_1", unique=True)]

    class ModelRepository(compose.repository.MongoRepository[Model]):
        __collection_name__ = "model"
        __indexes__ = indexes

    ModelRepository(fake_collection).ensure_indexes()

    fake_collection.create_indexes.assert_called_once_with(indexes)


def test_ensure_indexes_skip_when_no_indexes_declared(fake_collection: mock.Mock):
    class ModelRepository(compose.repository.MongoRepository[Model]):
        __collection_name__ = "model"

    ModelRepository(fake_collection).ensure_indexes()

    fake_collection.create_indexes.assert_not_called()


def test_setup_indexes_apply_each_repository_to_its_own_collection():
    primary_collection = mock.Mock(spec=Collection)
    archive_collection = mock.Mock(spec=Collection)
    primary_indexes = [pymongo.IndexModel([("google_sub", 1)], name="google_sub_1", unique=True)]

    class PrimaryUserRepository(compose.repository.MongoRepository[Model]):
        __collection_name__ = "user"
        __indexes__ = primary_indexes

    class ArchiveUserRepository(compose.repository.MongoRepository[Model]):
        __collection_name__ = "user"

    compose.repository.setup_indexes(
        PrimaryUserRepository(primary_collection),
        ArchiveUserRepository(archive_collection),
    )

    primary_collection.create_indexes.assert_called_once_with(primary_indexes)
    archive_collection.create_indexes.assert_not_called()

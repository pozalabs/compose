import pymongo

import compose


class Model(compose.entity.MongoEntity):
    name: str


def test_ensure_indexes_register_declared_indexes_on_bound_collection(
    mongo_client: pymongo.MongoClient,
):
    database = mongo_client.get_database("test_ensure_indexes")
    database.drop_collection("model")

    class ModelRepository(compose.repository.MongoRepository[Model]):
        __collection_name__ = "model"
        __indexes__ = [pymongo.IndexModel([("name", 1)], name="name_1", unique=True)]

    ModelRepository.create(database).ensure_indexes()

    indexes = database.get_collection("model").index_information()
    assert "name_1" in indexes
    assert indexes["name_1"]["key"] == [("name", 1)]
    assert indexes["name_1"]["unique"] is True


def test_setup_indexes_isolate_repositories_bound_to_different_databases(
    mongo_client: pymongo.MongoClient,
):
    primary_db = mongo_client.get_database("test_setup_indexes_primary")
    archive_db = mongo_client.get_database("test_setup_indexes_archive")
    primary_db.drop_collection("user")
    archive_db.drop_collection("user")

    class PrimaryUserRepository(compose.repository.MongoRepository[Model]):
        __collection_name__ = "user"
        __indexes__ = [pymongo.IndexModel([("name", 1)], name="name_1", unique=True)]

    class ArchiveUserRepository(compose.repository.MongoRepository[Model]):
        __collection_name__ = "user"

    archive_db.create_collection("user")

    compose.repository.setup_indexes(
        PrimaryUserRepository.create(primary_db),
        ArchiveUserRepository.create(archive_db),
    )

    primary_indexes = primary_db.get_collection("user").index_information()
    archive_indexes = archive_db.get_collection("user").index_information()
    assert "name_1" in primary_indexes
    assert set(archive_indexes) == {"_id_"}


def test_ensure_indexes_is_idempotent(mongo_client: pymongo.MongoClient):
    database = mongo_client.get_database("test_ensure_indexes_idempotent")
    database.drop_collection("model")

    class ModelRepository(compose.repository.MongoRepository[Model]):
        __collection_name__ = "model"
        __indexes__ = [pymongo.IndexModel([("name", 1)], name="name_1", unique=True)]

    repository = ModelRepository.create(database)
    repository.ensure_indexes()
    repository.ensure_indexes()

    indexes = database.get_collection("model").index_information()
    assert set(indexes) == {"_id_", "name_1"}

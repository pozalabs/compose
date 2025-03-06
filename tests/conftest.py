import os

import pymongo
import pytest

import compose

pytest_plugins = [
    "compose.testing.plugin.test_type_marker",
]


mongodb = compose.testcontainers.MongoDbContainer("mongo:8.0")


@pytest.fixture(scope="session")
def mongodb_container(request: pytest.FixtureRequest):
    mongodb.start()
    request.addfinalizer(mongodb.stop)

    os.environ["MONGO_URI"] = mongodb.get_connection_url()
    os.environ["MONGO_USERNAME"] = mongodb.username
    os.environ["MONGO_PASSWORD"] = mongodb.password

    yield mongodb


@pytest.fixture
def mongo_client(mongodb_container: compose.testcontainers.MongoDbContainer) -> pymongo.MongoClient:
    return pymongo.MongoClient(mongodb_container.get_connection_url())

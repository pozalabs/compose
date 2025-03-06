import pytest

import compose

pytest_plugins = [
    "compose.testing.plugin.test_type_marker",
]


mongodb = compose.testcontainers.MongoDbContainer("mongo:8.0").with_replica_set()


@pytest.fixture(scope="function")
def mongo_container(request: pytest.FixtureRequest):
    mongodb.start()
    request.addfinalizer(mongodb.stop)

    yield mongodb

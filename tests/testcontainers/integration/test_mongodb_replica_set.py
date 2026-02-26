import pymongo
import pytest

import compose

mongodb = compose.testcontainers.MongoDbContainer("mongo:8.0").with_replica_set()


@pytest.fixture(scope="module")
def mongo_client(request: pytest.FixtureRequest) -> pymongo.MongoClient:
    mongodb.start()
    request.addfinalizer(mongodb.stop)

    return pymongo.MongoClient(mongodb.get_connection_url())


def test_transaction_commit(mongo_client: pymongo.MongoClient):
    collection = mongo_client.test.accounts

    with mongo_client.start_session() as session:
        with session.start_transaction():
            collection.insert_one({"name": "alice", "balance": 100}, session=session)

    assert collection.find_one({"name": "alice"})["balance"] == 100


def test_transaction_abort(mongo_client: pymongo.MongoClient):
    collection = mongo_client.test.transfers

    with mongo_client.start_session() as session:
        with session.start_transaction():
            collection.insert_one({"name": "bob", "amount": 50}, session=session)
            session.abort_transaction()

    assert collection.find_one({"name": "bob"}) is None

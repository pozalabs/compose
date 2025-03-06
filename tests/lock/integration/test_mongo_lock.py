import concurrent.futures
import time

import pymongo

import compose

# mongodb = MongoDbContainer("mongo:7.0.0")
#
#
# @pytest.fixture(scope="module", autouse=True)
# def setup_mongodb(request: pytest.FixtureRequest):
#     mongodb.start()
#
#     def remove_container() -> None:
#         mongodb.stop()
#
#     request.addfinalizer(remove_container)
#
#     os.environ["MONGO_URI"] = mongodb.get_connection_url()
#     os.environ["MONGO_USERNAME"] = mongodb.username
#     os.environ["MONGO_PASSWORD"] = mongodb.password
#
#
# @pytest.fixture
# def mongo_client() -> pymongo.MongoClient:
#     return pymongo.MongoClient(
#         host=os.environ["MONGO_URI"],
#         username=os.environ["MONGO_USERNAME"],
#         password=os.environ["MONGO_PASSWORD"],
#     )
#
#
# @pytest.fixture
# def mongo_database(mongo_client: pymongo.MongoClient) -> Database:
#     return mongo_client.get_database("test")


class Bank:
    def __init__(self, lock_factory: compose.lock.MongoLockAcquirer):
        self.balance = 0
        self.lock_factory = lock_factory

    def deposit(self, amount):
        with self.lock_factory(key="bank_lock"):
            self._deposit(amount)

    def _deposit(self, amount):
        balance = self.balance
        balance += amount
        time.sleep(0.1)
        self.balance = balance


def test_lock(mongo_client: pymongo.MongoClient):
    db = mongo_client.get_database("test")

    bank = Bank(lock_factory=compose.lock.MongoLock.acquirer(db=db))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for money in [100] * 10:
            f = executor.submit(bank.deposit, amount=money)
            futures.append(f)

        for f in futures:
            f.result()

    assert bank.balance == 1000

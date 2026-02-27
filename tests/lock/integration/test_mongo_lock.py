import concurrent.futures
import time

import pymongo
import pytest

import compose
from compose.lock import LockAcquisitionFailedError


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


def test_cannot_acquire_lock_after_timeout(mongo_client: pymongo.MongoClient):
    db = mongo_client.get_database("test")
    acquirer = compose.lock.MongoLock.acquirer(db=db)

    holder = acquirer(key="timeout_test")
    holder.acquire()
    try:
        with pytest.raises(LockAcquisitionFailedError):
            with acquirer(
                key="timeout_test",
                timeout=compose.types.Seconds(0.3),
                lock_acquisition_interval=compose.types.Seconds(0.05),
            ):
                pass
    finally:
        holder.release()


def test_lock_reacquired_after_auto_release(mongo_client: pymongo.MongoClient):
    db = mongo_client.get_database("test")
    acquirer = compose.lock.MongoLock.acquirer(db=db)

    lock = acquirer(key="auto_release_test", auto_release_after=compose.types.Seconds(0.5))
    assert lock.acquire()

    time.sleep(0.6)

    reacquired = acquirer(key="auto_release_test", timeout=compose.types.Seconds(1))
    assert reacquired.acquire()
    reacquired.release()


def test_ttl_index_created_on_expires_at(mongo_client: pymongo.MongoClient):
    db = mongo_client.get_database("test")
    collection_name = "test_ttl_index"
    compose.lock.MongoLock.acquirer(db=db, collection_name=collection_name)

    indexes = db[collection_name].index_information()
    index = indexes[compose.lock.MongoLock.index_name]
    assert index["key"] == [("expires_at", 1)]
    assert index["expireAfterSeconds"] == 0


def test_ttl_index_creation_is_idempotent(mongo_client: pymongo.MongoClient):
    db = mongo_client.get_database("test")
    collection_name = "test_ttl_idempotent"
    compose.lock.MongoLock.acquirer(db=db, collection_name=collection_name)
    compose.lock.MongoLock.acquirer(db=db, collection_name=collection_name)

    index_name = compose.lock.MongoLock.index_name
    indexes = db[collection_name].index_information()
    assert index_name in indexes

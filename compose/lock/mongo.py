import functools
import time
import types
from typing import ClassVar, NewType, Protocol, Self

import pendulum
import pymongo
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from .exceptions import LockAcquisitionFailedError

Seconds = NewType("Seconds", float)


class MongoLockAcquirer(Protocol):
    def __call__(
        self,
        key: str,
        auto_release_after: Seconds = Seconds(60),
        timeout: Seconds = Seconds(60),
        lock_acquisition_interval: Seconds = Seconds(0.1),
    ) -> Self: ...


class MongoLock:
    default_collection_name: ClassVar[str] = "compose.lock"
    index_name: ClassVar[str] = "expires_at_ttl"

    def __init__(
        self,
        key: str,
        collection: Collection,
        auto_release_after: Seconds = Seconds(60),
        timeout: Seconds = Seconds(60),
        lock_acquisition_interval: Seconds = Seconds(0.1),
    ):
        self.key = key
        self.collection = collection
        self.auto_release_after = auto_release_after
        self.timeout = timeout
        self.lock_acquisition_interval = lock_acquisition_interval

    @classmethod
    def _ensure_ttl_index(cls, collection: Collection) -> None:
        current_index = collection.index_information()
        if cls.index_name not in current_index:
            collection.create_index(
                [("expires_at", pymongo.ASCENDING)],
                name=cls.index_name,
                expireAfterSeconds=0,
            )

    @classmethod
    def acquirer(cls, db: Database, collection_name: str | None = None) -> MongoLockAcquirer:
        collection_name = collection_name or cls.default_collection_name
        collection = db[collection_name]
        cls._ensure_ttl_index(collection)
        return functools.partial(cls, collection=collection)

    def __enter__(self) -> Self:
        if self.acquire():
            return self

        raise LockAcquisitionFailedError(f"Failed to acquire lock for key: {self.key}")

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        self.release()

    def acquire(self) -> bool:
        start_time = pendulum.DateTime.utcnow()
        try_until = start_time.add(seconds=self.timeout)

        while True:
            expires_at = pendulum.DateTime.utcnow().add(seconds=self.auto_release_after)
            try:
                lock = self.collection.find_one_and_update(
                    {
                        "_id": self.key,
                        "expires_at": {"$lt": pendulum.DateTime.utcnow()},
                    },
                    {"$set": {"expires_at": expires_at}},
                    upsert=True,
                    return_document=pymongo.ReturnDocument.AFTER,
                )
                # MongoDB는 Date 타입에서 나노초를 버리기 때문에 <=로 비교
                if pendulum.instance(lock["expires_at"], tz=pendulum.UTC) <= expires_at:
                    return True

            except DuplicateKeyError:
                pass

            if pendulum.DateTime.utcnow() > try_until:
                return False

            time.sleep(self.lock_acquisition_interval)

    def release(self) -> None:
        self.collection.delete_one({"_id": self.key})

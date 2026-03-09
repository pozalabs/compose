import pendulum
import pymongo
from dishka import Provider, Scope, make_async_container, provide
from pymongo.database import Database

from src.user.dependency import UserProvider


class InfraProvider(Provider):
    scope = Scope.APP

    @provide
    def mongo_client(self) -> pymongo.MongoClient:
        return pymongo.MongoClient(
            host="mongodb://admin:admin@db:27017",
            tz_aware=True,
            tzinfo=pendulum.UTC,
        )

    @provide
    def database(self, client: pymongo.MongoClient) -> Database:
        return client.get_database("compose-example")


container = make_async_container(InfraProvider(), UserProvider())

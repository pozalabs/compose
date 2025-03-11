import pendulum
import pymongo
from dependency_injector import providers

import compose
from src.user.dependency import UserContainer

PACKAGES = {
    "src.user",
}


class ApplicationContainer(compose.dependency.DeclarativeContainer):
    mongo_client = providers.Singleton(
        pymongo.MongoClient,
        host="mongodb://admin:admin@db:27017",
        tz_aware=True,
        tzinfo=pendulum.UTC,
    )
    database = providers.Factory(
        mongo_client.provided.get_database.call(),
        name="compose-example",
    )

    user = providers.Container(UserContainer, database=database)


wirer = compose.dependency.create_wirer(packages=PACKAGES)
provide = compose.dependency.create_provider(ApplicationContainer)

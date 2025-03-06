import pendulum
import pymongo
from pymongo.client_session import ClientSession

import compose


class User(compose.entity.Entity):
    name: str


class UserRepository(compose.repository.MongoRepository[User]):
    __collection_name__ = "user"


class AddUser(compose.command.Command):
    name: str


class AddUserHandler:
    def __init__(self, user_repository: UserRepository, uow: compose.uow.MongoUnitOfWork):
        self.user_repository = user_repository
        self.uow = uow

    @compose.uow.mongo_transactional
    def handle(self, cmd: AddUser, session: ClientSession) -> User:
        user = User(
            id=compose.types.PyObjectId(b"test-user-01"),
            name=cmd.name,
            created_at=pendulum.datetime(2025, 3, 6),
            updated_at=pendulum.datetime(2025, 3, 6),
        )
        self.user_repository.add(user, session=session)
        return self.user_repository.find_by({"name": user.name}, session=session)


# mongodb = compose.testcontainers.MongoDbContainer("mongo:8.0.0").with_replica_set()
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


def test_transaction(mongo_client: pymongo.MongoClient):
    handler = AddUserHandler(
        user_repository=UserRepository.create(mongo_client.get_database("test")),
        uow=compose.uow.MongoUnitOfWork(mongo_client.start_session),
    )
    actual = handler.handle(AddUser(name="test"))

    expected = User(
        id=compose.types.PyObjectId(b"test-user-01"),
        name="test",
        created_at=pendulum.datetime(2025, 3, 6),
        updated_at=pendulum.datetime(2025, 3, 6),
    )

    assert actual == expected

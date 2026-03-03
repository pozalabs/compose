from collections.abc import Generator
from typing import ClassVar

import pendulum
import pytest
from sqlalchemy import Column, MetaData, String, Table, create_engine
from sqlalchemy.orm import Session, sessionmaker

import compose
from compose.repository.sql import SQLRepository

metadata = MetaData()

user_table = Table(
    "users",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("name", String(50)),
    Column("created_at", String),
    Column("updated_at", String),
)


class User(compose.entity.SQLEntity):
    name: str

    updatable_fields: ClassVar[set[str]] = {"name"}


class UserRepository(SQLRepository[User]):
    __table__: ClassVar[Table] = user_table


@pytest.fixture
def engine():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine) -> Generator[Session, None, None]:
    session_factory = sessionmaker(bind=engine)
    with session_factory() as session:
        yield session


@pytest.fixture
def repository() -> UserRepository:
    return UserRepository()


def test_add_and_find_by_id(repository: UserRepository, session: Session):
    user = User(name="alice")

    repository.add(user, session)
    session.commit()

    found = repository.find_by_id(user.id, session)
    assert found is not None
    assert found.name == "alice"


def test_find_by(repository: UserRepository, session: Session):
    user = User(name="bob")
    repository.add(user, session)
    session.commit()

    found = repository.find_by({"name": "bob"}, session)
    assert found is not None
    assert found.name == "bob"


def test_find_by_return_none_when_not_found(repository: UserRepository, session: Session):
    found = repository.find_by({"name": "nonexistent"}, session)
    assert found is None


def test_list_by(repository: UserRepository, session: Session):
    repository.add(User(name="charlie"), session)
    repository.add(User(name="charlie"), session)
    repository.add(User(name="dave"), session)
    session.commit()

    results = repository.list_by({"name": "charlie"}, session)
    assert len(results) == 2
    assert all(u.name == "charlie" for u in results)


def test_list_by_with_sort(repository: UserRepository, session: Session):
    repository.add(User(name="banana"), session)
    repository.add(User(name="apple"), session)
    repository.add(User(name="cherry"), session)
    session.commit()

    asc_results = repository.list_by({}, session, sort=[("name", 1)])
    assert [u.name for u in asc_results] == ["apple", "banana", "cherry"]

    desc_results = repository.list_by({}, session, sort=[("name", -1)])
    assert [u.name for u in desc_results] == ["cherry", "banana", "apple"]


def test_update(repository: UserRepository, session: Session):
    user = User(name="eve")
    repository.add(user, session)
    session.commit()

    before_updated_at = user.updated_at
    user.update(name="eve-updated")
    repository.update(user, session)
    session.commit()

    found = repository.find_by_id(user.id, session)
    assert found is not None
    assert found.name == "eve-updated"
    assert pendulum.instance(found.updated_at) >= pendulum.instance(before_updated_at)


def test_delete(repository: UserRepository, session: Session):
    user = User(name="frank")
    repository.add(user, session)
    session.commit()

    repository.delete(user.id, session)
    session.commit()

    found = repository.find_by_id(user.id, session)
    assert found is None

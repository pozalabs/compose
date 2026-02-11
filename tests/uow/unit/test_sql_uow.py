from typing import ClassVar

import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine
from sqlalchemy.orm import Session, sessionmaker

import compose
from compose.repository.sql import SQLRepository
from compose.uow.sql import SQLUnitOfWork, sql_transactional

metadata = MetaData()

item_table = Table(
    "items",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(50)),
    Column("created_at", String),
    Column("updated_at", String),
)


class Item(compose.entity.SQLEntity):
    name: str


class ItemRepository(SQLRepository[Item]):
    __table__: ClassVar[Table] = item_table


@pytest.fixture
def engine():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine)


@pytest.fixture
def uow(session_factory) -> SQLUnitOfWork:
    return SQLUnitOfWork(session_factory)


def test_with_transaction_commit(uow: SQLUnitOfWork, session_factory: sessionmaker[Session]):
    repo = ItemRepository()

    def create_item(session: Session) -> Item:
        item = Item(name="test-item")
        repo.add(item, session)
        return item

    result = uow.with_transaction(create_item)

    assert result.id is not None
    with session_factory() as session:
        found = repo.find_by_id(result.id, session)
        assert found is not None
        assert found.name == "test-item"


def test_with_transaction_rollback_on_exception(
    uow: SQLUnitOfWork, session_factory: sessionmaker[Session]
):
    repo = ItemRepository()

    def create_and_fail(session: Session) -> None:
        item = Item(name="should-not-persist")
        repo.add(item, session)
        raise RuntimeError("intentional error")

    with pytest.raises(RuntimeError, match="intentional error"):
        uow.with_transaction(create_and_fail)

    with session_factory() as session:
        results = repo.list_by({}, session)
        assert len(results) == 0


def test_sql_transactional_decorator(uow: SQLUnitOfWork, session_factory: sessionmaker[Session]):
    repo = ItemRepository()

    class ItemService:
        def __init__(self, uow: SQLUnitOfWork):
            self.uow = uow

        @sql_transactional
        def create_item(self, name: str, session: Session) -> Item:
            item = Item(name=name)
            repo.add(item, session)
            return item

    service = ItemService(uow)
    result = service.create_item(name="decorated-item")

    assert result.id is not None
    with session_factory() as session:
        found = repo.find_by_id(result.id, session)
        assert found is not None
        assert found.name == "decorated-item"

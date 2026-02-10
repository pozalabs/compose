from typing import Any
from unittest import mock

import pytest
from pymongo.collection import Collection

import compose


class Model(compose.entity.Entity):
    name: str
    status: str


class ModelRepository(compose.repository.MongoRepository[Model]):
    __collection_name__ = "model"

    find_by_name = compose.repository.finder("name")
    list_by_status = compose.repository.lister("status")


@pytest.fixture
def model_data() -> dict[str, Any]:
    return dict(
        id=compose.types.PyObjectId(b"test-id-0001"),
        name="name01",
        status="active",
        created_at=compose.types.DateTime(2023, 1, 13),
        updated_at=compose.types.DateTime(2023, 1, 13),
    )


@pytest.fixture
def fake_collection(model_data: dict[str, Any]) -> Collection:
    collection = mock.Mock(spec=Collection)
    collection.find_one = mock.Mock(return_value=model_data)
    collection.find = mock.Mock(return_value=[model_data])
    return collection


@pytest.fixture
def fake_repo(fake_collection: Collection) -> ModelRepository:
    return ModelRepository(fake_collection)


def test_finder_delegate_to_find_by(
    fake_repo: ModelRepository,
    fake_collection: Collection,
):
    fake_repo.find_by_name("name01")

    fake_collection.find_one.assert_called_once_with(
        filter={"name": "name01"},
        session=None,
    )


def test_finder_pass_session(
    fake_repo: ModelRepository,
    fake_collection: Collection,
):
    session = mock.Mock()
    fake_repo.find_by_name("name01", session=session)

    fake_collection.find_one.assert_called_once_with(
        filter={"name": "name01"},
        session=session,
    )


def test_finder_return_entity(
    fake_repo: ModelRepository,
    model_data: dict[str, Any],
):
    result = fake_repo.find_by_name("name01")

    assert isinstance(result, Model)
    assert result.name == model_data["name"]


def test_finder_return_none_when_not_found(
    fake_repo: ModelRepository,
    fake_collection: Collection,
):
    fake_collection.find_one.return_value = None

    result = fake_repo.find_by_name("nonexistent")

    assert result is None


def test_lister_delegate_to_list_by(
    fake_repo: ModelRepository,
    fake_collection: Collection,
):
    fake_repo.list_by_status("active")

    fake_collection.find.assert_called_once_with(
        filter={"status": "active"},
        projection=None,
        sort=None,
        session=None,
    )


def test_lister_pass_sort(
    fake_repo: ModelRepository,
    fake_collection: Collection,
):
    fake_repo.list_by_status("active", sort=[("created_at", -1)])

    fake_collection.find.assert_called_once_with(
        filter={"status": "active"},
        projection=None,
        sort=[("created_at", -1)],
        session=None,
    )


def test_lister_pass_session(
    fake_repo: ModelRepository,
    fake_collection: Collection,
):
    session = mock.Mock()
    fake_repo.list_by_status("active", session=session)

    fake_collection.find.assert_called_once_with(
        filter={"status": "active"},
        projection=None,
        sort=None,
        session=session,
    )


def test_lister_return_entity_list(
    fake_repo: ModelRepository,
    model_data: dict[str, Any],
):
    result = fake_repo.list_by_status("active")

    assert result == [Model(**model_data)]

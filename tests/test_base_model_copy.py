from typing import Any

import pytest

from compose.container import BaseModel


class Model(BaseModel):
    name: str


class ModelWithDefault(Model):
    age: int = 10


@pytest.fixture
def model() -> BaseModel:
    return Model(name="name")


@pytest.fixture
def model_with_default() -> BaseModel:
    return ModelWithDefault(name="name")


@pytest.mark.parametrize(
    "update, expected",
    [(dict(name="name", age=20), ModelWithDefault(name="name", age=20))],
    ids=("명시적으로 초기화하지 않은 필드가 있어도 필드 값 변경 가능",),
)
def test_copy_model_with_default(
    model_with_default: ModelWithDefault, update: dict[str, Any], expected: ModelWithDefault
):
    assert model_with_default.copy(update=update) == expected


def test_cannot_copy_with_undefined_fields(model: Model):
    with pytest.raises(AttributeError):
        model.copy(update=dict(name="name", age=10))

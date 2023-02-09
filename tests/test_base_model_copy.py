from typing import Any

import pytest

from compose.container import BaseModel


class Model(BaseModel):
    name: str


class Child(Model):
    age: int = 10


@pytest.fixture
def model() -> BaseModel:
    return Model(name="name")


@pytest.fixture
def child() -> BaseModel:
    return Child(name="name", age=10)


@pytest.mark.parametrize(
    "update, expected",
    [
        (
            dict(name="name", age=20),
            Child(name="name", age=20),
        )
    ],
)
def test_copy_model_with_defaults(child: Child, update: dict[str, Any], expected: Child):
    assert child.copy(update=update) == expected


def test_cannot_copy_with_undefined_fields(model: Model):
    with pytest.raises(AttributeError):
        model.copy(update=dict(name="name", age=10))

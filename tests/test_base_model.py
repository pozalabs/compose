from collections.abc import Callable

import pytest
from pydantic import ValidationError

import compose


class Model(compose.BaseModel):
    name: str


class SchemaModel(compose.schema.Schema):
    name: str


@pytest.mark.parametrize(
    "copy_model",
    [
        lambda model: model.copy(
            update={"name": [1, 2, 3]},
            validate=True,
        ),
        lambda model: model.model_copy(
            update={"name": [1, 2, 3]},
            validate=True,
        ),
    ],
    ids=("copy", "model_copy"),
)
def test_validate_on_copy(copy_model: Callable[[Model], Model]):
    model = Model(name="test")

    with pytest.raises(ValidationError):
        copy_model(model)


def test_from_model():
    model = Model(name="test")
    actual = SchemaModel.from_model(model)
    expected = SchemaModel(name="test")

    assert actual == expected

import pytest

from compose.container import BaseModel


@pytest.fixture
def model() -> BaseModel:
    class Model(BaseModel):
        name: str

    return Model(name="name")


def test_cannot_copy_with_undefined_fields(model: BaseModel):
    with pytest.raises(AttributeError):
        model.copy(update=dict(name="name", age=10))

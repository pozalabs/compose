import compose


def test_model_dump():
    class Model(compose.BaseModel):
        name: str

    assert compose.compat.model_dump(Model(name="test")) == {"name": "test"}

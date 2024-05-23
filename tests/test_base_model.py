import compose


class Model(compose.BaseModel):
    name: str


class SchemaModel(compose.schema.Schema):
    name: str


def test_model_validate():
    model = Model(name="test")
    assert SchemaModel.model_validate(model.dict()) == SchemaModel(name="test")

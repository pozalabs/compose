from compose.query.mongo.op import Spec


def test_exclude():
    spec = Spec.include("field")

    assert spec.expression() == {"field": 1}

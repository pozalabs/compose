from compose.query.mongo.op import Spec


def test_exclude():
    spec = Spec.exclude("field")

    assert spec.expression() == {"field": 0}

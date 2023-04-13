from compose.query.mongo.op import SortBy


def test_asc_expression():
    assert SortBy.asc("field").expression() == {"field": 1}


def test_desc_expression():
    assert SortBy.desc("field").expression() == {"field": -1}

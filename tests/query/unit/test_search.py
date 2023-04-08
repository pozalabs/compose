import pytest

from compose.query.mongo.op import DictExpression, Operator, Search, TextSearchOperator


@pytest.fixture
def text_search_operator() -> TextSearchOperator:
    return TextSearchOperator(query="q", path=["field_1", "field_2"])


@pytest.fixture
def op(request: pytest.FixtureRequest) -> Operator:
    fixture_name: str = getattr(request, "param", "text_search_operator")
    return request.getfixturevalue(fixture_name)


@pytest.mark.parametrize(
    "index, op, expected",
    [
        (
            "default",
            "text_search_operator",
            {
                "$search": {
                    "index": "default",
                    "$text": {"query": "q", "path": ["field_1", "field_2"]},
                }
            },
        ),
    ],
    indirect=["op"],
    ids=("$text 연산자 표현식",),
)
def test_expression(index: str, op: Operator, expected: DictExpression):
    assert Search(index=index, op=op).expression() == expected

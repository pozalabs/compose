import pytest

from compose.query.mongo.op import DictExpression, Pagination, Set, Specification


@pytest.mark.parametrize(
    "pagination, expected",
    [
        (
            Pagination(page=1, per_page=10),
            {
                "$facet": {
                    "metadata": [{"$count": "total"}],
                    "items": [{"$skip": 0}, {"$limit": 10}],
                }
            },
        ),
        (
            Pagination(),
            {"$facet": {"metadata": [{"$count": "total"}], "items": []}},
        ),
        (
            Pagination(
                page=1,
                per_page=10,
                metadata_ops=[Set(Specification(field="field", spec="value"))],
            ),
            {
                "$facet": {
                    "metadata": [{"$count": "total"}, {"$set": {"field": "value"}}],
                    "items": [{"$skip": 0}, {"$limit": 10}],
                }
            },
        ),
    ],
    ids=(
        "페이지네이션을 수행하는 경우",
        "페이지네이션을 수행하지 않는 경우",
        "metadata 필드에 추가 필드를 설정하는 경우",
    ),
)
def test_pagination_expression(pagination: Pagination, expected: DictExpression):
    assert pagination.expression() == expected

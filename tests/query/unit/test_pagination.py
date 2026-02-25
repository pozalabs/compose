import pytest

from compose.query.mongo.op import DictExpression, OffsetPagination, Set, Spec


@pytest.mark.parametrize(
    "pagination, expected",
    [
        (
            OffsetPagination(page=1, per_page=10),
            {
                "$facet": {
                    "metadata": [{"$count": "total"}],
                    "items": [{"$skip": 0}, {"$limit": 10}],
                }
            },
        ),
        (
            OffsetPagination(
                page=1,
                per_page=10,
                metadata_ops=[Set(Spec(field="field", spec="value"))],
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
        "metadata 필드에 추가 필드를 설정하는 경우",
    ),
)
def test_pagination_expression(pagination: OffsetPagination, expected: DictExpression):
    assert pagination.expression() == expected

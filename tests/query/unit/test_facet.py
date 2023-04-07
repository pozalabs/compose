import pymongo
import pytest

from compose.query.mongo.op import (
    DictExpression,
    Eq,
    Facet,
    FacetSpecification,
    Match,
    Sort,
    SortBy,
)


@pytest.fixture
def specs() -> list[FacetSpecification]:
    return [
        FacetSpecification(
            output_field="output_field_1",
            stages=[
                Match.and_(Eq(field="field_1", value="value_1")),
                Sort(SortBy(field="field_1", direction=pymongo.ASCENDING)),
            ],
        ),
        FacetSpecification(
            stages=[
                Match.and_(Eq(field="field_2", value="value_2")),
                Sort(SortBy(field="field_2", direction=pymongo.ASCENDING)),
            ],
            output_field="output_field_2",
        ),
    ]


@pytest.fixture
def expected() -> DictExpression:
    return {
        "$facet": {
            "output_field_1": [
                {"$match": {"$and": [{"field_1": {"$eq": "value_1"}}]}},
                {"$sort": {"field_1": pymongo.ASCENDING}},
            ],
            "output_field_2": [
                {"$match": {"$and": [{"field_2": {"$eq": "value_2"}}]}},
                {"$sort": {"field_2": pymongo.ASCENDING}},
            ],
        }
    }


def test_expression(specs: list[FacetSpecification], expected: DictExpression):
    assert Facet(*specs).expression() == expected

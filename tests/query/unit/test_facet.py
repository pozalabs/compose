import pymongo
import pytest

from compose.query.mongo.op import (
    DictExpression,
    Eq,
    Facet,
    FacetSubPipeline,
    Match,
    Pipeline,
    Sort,
    SortBy,
)


@pytest.fixture
def specs() -> list[FacetSubPipeline]:
    return [
        FacetSubPipeline(
            output_field="output_field_1",
            pipeline=Pipeline(
                Match.and_(Eq(field="field_1", value="value_1")),
                Sort(SortBy(field="field_1", direction=pymongo.ASCENDING)),
            ),
        ),
        FacetSubPipeline(
            output_field="output_field_2",
            pipeline=Pipeline(
                Match.and_(Eq(field="field_2", value="value_2")),
                Sort(SortBy(field="field_2", direction=pymongo.ASCENDING)),
            ),
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


def test_expression(specs: list[FacetSubPipeline], expected: DictExpression):
    assert Facet(*specs).expression() == expected

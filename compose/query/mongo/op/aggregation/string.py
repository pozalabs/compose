from ..base import GeneralAggregationOperator


class Concat(GeneralAggregationOperator):
    mongo_operator = "$concat"

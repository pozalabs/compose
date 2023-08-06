from ..base import GeneralAggregationOperator


class Concat(GeneralAggregationOperator):
    mongo_operator = "$concat"


class ToString(GeneralAggregationOperator):
    mongo_operator = "$toString"

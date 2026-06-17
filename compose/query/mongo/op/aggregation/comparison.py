from .base import create_general_aggregation_operator

AEq = create_general_aggregation_operator(name="AEq", mongo_operator="$eq")
ANe = create_general_aggregation_operator(name="ANe", mongo_operator="$ne")
AGt = create_general_aggregation_operator(name="AGt", mongo_operator="$gt")
AGte = create_general_aggregation_operator(name="AGte", mongo_operator="$gte")
ALt = create_general_aggregation_operator(name="ALt", mongo_operator="$lt")
ALte = create_general_aggregation_operator(name="ALte", mongo_operator="$lte")

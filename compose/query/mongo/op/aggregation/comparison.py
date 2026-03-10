from .. import utils

AEq = utils.create_general_aggregation_operator(name="AEq", mongo_operator="$eq")
ANe = utils.create_general_aggregation_operator(name="ANe", mongo_operator="$ne")
AGt = utils.create_general_aggregation_operator(name="AGt", mongo_operator="$gt")
AGte = utils.create_general_aggregation_operator(name="AGte", mongo_operator="$gte")
ALt = utils.create_general_aggregation_operator(name="ALt", mongo_operator="$lt")
ALte = utils.create_general_aggregation_operator(name="ALte", mongo_operator="$lte")

from __future__ import annotations

from .. import utils

AIn = utils.create_general_aggregation_operator(name="AIn", mongo_operator="$in")

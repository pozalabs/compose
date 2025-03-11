from typing import Any

from .base import Operator
from .func import Merge


def Q(*ops: *tuple[Operator, ...]) -> dict[str, Any]:
    return Merge.dict(*ops).expression()

from typing import Any

from .base import Merge, Operator


def Q(*ops: *tuple[Operator, ...]) -> dict[str, Any]:
    return Merge.dict(*ops).expression()

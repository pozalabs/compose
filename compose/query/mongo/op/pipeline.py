from typing import Any

from .base import Operator, OpFilter, Stage


class Pipeline(Operator):
    def __init__(self, *stages: Stage):
        self.stages = list(stages)

    def expression(self) -> list[dict[str, Any]]:
        return OpFilter.non_empty(*self.stages).expression()

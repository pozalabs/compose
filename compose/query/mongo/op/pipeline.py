from typing import Any

from .base import Operator
from .stage import Stage


class Pipeline(Operator):
    def __init__(self, *stages: Stage):
        self.stages = list(stages)

    def expression(self) -> list[dict[str, Any]]:
        return [expression for stage in self.stages if (expression := stage.expression())]

from __future__ import annotations

import abc
from typing import Any


class Operator:
    @abc.abstractmethod
    def expression(self) -> Any:
        raise NotImplementedError

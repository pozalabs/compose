import base64
import json
from collections.abc import Callable
from typing import Any

import pymongo

from .comparison import Gt, Lt
from .pipeline import Pipeline
from .stage import Limit, Match, Sort, Stage
from .types import DictExpression, ListExpression


class CursorEncoder:
    def __init__(
        self,
        cursor_keys: list[str],
        json_encoder: type[json.JSONEncoder] | None = None,
    ):
        self.cursor_keys = cursor_keys
        self.json_encoder = json_encoder or json.JSONEncoder

    def encode(self, document: dict[str, Any]) -> str:
        cursor_params = {key: document[key] for key in self.cursor_keys}
        return base64.b64encode(json.dumps(cursor_params, cls=self.json_encoder).encode()).decode()


class CursorDecoder:
    def __init__(self, parsers: dict[str, Callable[[Any], Any]] | None = None):
        self.parsers = parsers or {}

    def decode(self, cursor: str) -> dict[str, Any]:
        decoded = json.loads(base64.b64decode(cursor).decode())
        return {key: self.parsers.get(key, lambda x: x)(value) for key, value in decoded.items()}


class AfterCursor(Stage[DictExpression]):
    direction_to_op = {pymongo.ASCENDING: Gt, pymongo.DESCENDING: Lt}

    def __init__(self, sort: Sort, cursor_decoder: CursorDecoder, cursor: str | None = None):
        self.sort = sort
        self.cursor_decoder = cursor_decoder
        self.cursor = cursor

    def expression(self) -> DictExpression:
        if self.cursor is None:
            return {}

        cursor_params = self.cursor_decoder.decode(self.cursor)
        return Match.nor(
            *(
                self.direction_to_op[criterion.direction](
                    field=criterion.field,
                    value=cursor_params[criterion.field],
                )
                for criterion in self.sort.criteria
            )
        ).expression()


class CursorPagination(Stage[ListExpression]):
    def __init__(
        self,
        sort: Sort,
        cursor_decoder: CursorDecoder,
        cursor: str | None | None = None,
        per_page: int | None = None,
    ):
        self.cursor_decoder = cursor_decoder
        self.sort = sort
        self.cursor = cursor
        self.per_page = per_page

    def expression(self) -> ListExpression:
        return Pipeline(
            AfterCursor(
                sort=self.sort,
                cursor_decoder=self.cursor_decoder,
                cursor=self.cursor,
            ),
            self.sort,
            Limit(self.per_page),
        ).expression()

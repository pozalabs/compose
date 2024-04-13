import http
from typing import Any

from fastapi import Response
from starlette.background import BackgroundTask


class NoContentResponse(Response):
    def __init__(
        self,
        content: Any = None,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(
            content=content,
            headers=headers,
            media_type=media_type,
            status_code=http.HTTPStatus.NO_CONTENT,
            background=background,
        )

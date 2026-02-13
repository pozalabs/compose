import os
from typing import Any

from pydantic import Field

from compose.container import BaseModel


class GunicornSettings(BaseModel):
    wsgi_app: str
    bind: str = "0.0.0.0:80"
    workers: int = Field(default_factory=lambda: os.cpu_count() + 1)
    worker_class: str = "uvicorn.UvicornWorker"
    threads: int = 2
    timeout: int = 120
    max_requests: int | None = None
    max_requests_jitter: int | None = None


def export_settings(
    globals_: dict[str, Any],
    settings: GunicornSettings,
    *,
    env: str | None = None,
    overrides: dict[str, dict[str, Any]] | None = None,
    **kwargs: Any,
) -> None:
    if env is not None and overrides and env in overrides:
        settings = settings.model_copy(update=overrides[env])
    globals_ |= settings.model_dump(exclude_none=True) | kwargs

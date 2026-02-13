from __future__ import annotations

import urllib.parse
from typing import Any, ClassVar, cast

from .primitive import Str


class _S3ObjectUrl(Str):
    base_url: ClassVar[str]

    def __new__(cls, v: Any):
        if getattr(cls, "base_url", None) is None:
            raise ValueError(
                f"`base_url` must be set on `{cls.__name__}`. "
                f"Use `create_s3_object_url()` to create a configured type"
            )

        key = _extract_key(str(v), base_url=cls.base_url)
        encoded_path = _encode_path(key)
        return super().__new__(cls, f"{cls.base_url}/{encoded_path}")


def create_s3_object_url(base_url: str) -> type[_S3ObjectUrl]:
    return cast(
        type[_S3ObjectUrl],
        type("S3ObjectUrl", (_S3ObjectUrl,), {"base_url": base_url}),
    )


def _extract_key(v: str, *, base_url: str) -> str:
    v = urllib.parse.unquote(v.strip("/"))
    return v.removeprefix(base_url).lstrip("/")


def _encode_path(key: str) -> str:
    return "/".join(urllib.parse.quote(part, safe="~()*!.'") for part in key.split("/"))

from collections.abc import Generator
from typing import Self

import httpx


class HeaderAuth(httpx.Auth):
    def __init__(self, headers: dict[str, str]) -> None:
        self.headers = headers

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        for key, value in self.headers.items():
            request.headers[key] = value
        yield request

    @classmethod
    def from_api_key(cls, api_key: str, header_name: str = "x-api-key") -> Self:
        return cls({header_name: api_key})

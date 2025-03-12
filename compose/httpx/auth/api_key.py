from collections.abc import Generator
from typing import Self

import httpx


class HeaderAPIKeyAuth(httpx.Auth):
    def __init__(self, *pairs: *tuple[tuple[str, str], ...]) -> None:
        self.pairs = list(pairs)

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        for key, value in dict(self.pairs).items():
            request.headers[key] = value

        yield request

    @classmethod
    def single(cls, key: str, header_name: str = "x-api-key") -> Self:
        return cls((header_name, key))

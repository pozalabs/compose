from collections.abc import Generator

import httpx


class HeaderAPIKeyAuth(httpx.Auth):
    def __init__(self, api_key: str, header_name: str = "X-API-Key"):
        self.api_key = api_key
        self.header_name = header_name

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers[self.header_name] = self.api_key
        yield request

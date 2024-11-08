import http
import secrets
from collections.abc import Callable
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyHeader as FastAPIAPIKeyHeader
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security import HTTPBearer as FastAPIHTTPBearer
from fastapi.security.base import SecurityBase
from starlette.exceptions import HTTPException as StarletteHTTPException


def unauthorized_error(detail: str, headers: dict[str, str] | None = None) -> HTTPException:
    return HTTPException(
        status_code=http.HTTPStatus.UNAUTHORIZED,
        detail=detail,
        headers=headers,
    )


class HTTPBasicAuth:
    def __init__(self, username: str, password: str, security: HTTPBasic):
        self.username = username
        self.password = password
        self.security = security

    def authenticator(self) -> Callable[[HTTPBasicCredentials], None]:
        security = self.security

        def compare_digest(a: str, b: str) -> bool:
            return secrets.compare_digest(a.encode(), b.encode())

        def authenticate(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> None:
            is_correct_username = compare_digest(credentials.username, self.username)
            is_correct_password = compare_digest(credentials.password, self.password)

            if not (is_correct_username and is_correct_password):
                raise HTTPException(
                    status_code=http.HTTPStatus.UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Basic"},
                )

        return authenticate


class APIKeyHeader(FastAPIAPIKeyHeader):
    def __init__(
        self,
        *,
        api_key: str,
        name: str = "X-API-Key",
        auto_error: bool = True,
        scheme_name: str | None = None,
        description: str | None = None,
    ):
        super().__init__(
            name=name,
            auto_error=auto_error,
            scheme_name=scheme_name,
            description=description,
        )
        self.api_key = api_key

    async def __call__(self, request: Request) -> str:
        exc = unauthorized_error(detail="Not authenticated. Invalid API key")

        try:
            input_api_key = await super().__call__(request)
        except (StarletteHTTPException, HTTPException):
            raise exc

        if input_api_key is None or input_api_key != self.api_key:
            raise exc

        return input_api_key


class HTTPBearer(FastAPIHTTPBearer):
    def __init__(
        self,
        *,
        auto_error: bool = True,
        error_handlers: dict[Literal["on_credentials_missing"], Callable[[], HTTPException]]
        | None = None,
    ):
        super().__init__(auto_error=auto_error)
        self.error_handlers = error_handlers or {}
        self._default_error_handler = lambda: unauthorized_error(detail="Not authenticated")

    async def __call__(self, request: Request) -> str:
        try:
            credentials = await super().__call__(request)
        except HTTPException:
            raise self.error_handlers.get("on_credentials_missing", self._default_error_handler)()

        return credentials.credentials


class CookieAuth(SecurityBase):
    def __init__(
        self,
        *,
        name: str,
        error_handlers: dict[Literal["on_cookie_missing"], Callable[[], HTTPException]]
        | None = None,
    ):
        self.name = name
        self.error_handlers = error_handlers or {}
        self._default_error_handler = lambda: unauthorized_error(detail="Not authenticated")

    async def __call__(self, request: Request) -> str:
        if (credentials := request.cookies.get(self.name)) is None:
            raise self.error_handlers.get("on_cookie_missing", self._default_error_handler)()

        return credentials

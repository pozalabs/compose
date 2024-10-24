import http
import secrets
from collections.abc import Callable
from typing import Annotated

from authlib.jose import JWTClaims
from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyHeader as FastAPIAPIKeyHeader
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
from starlette.exceptions import HTTPException as StarletteHTTPException

from compose import exceptions
from compose.auth import JWTDecoder


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


class JWTBearer(HTTPBearer):
    def __init__(
        self,
        token_decoder: JWTDecoder,
        on_token_lookup_error: Callable[[], HTTPException],
        on_token_decoding_error: Callable[[], HTTPException],
    ):
        super().__init__(auto_error=True)
        self.token_decoder = token_decoder
        self.on_token_lookup_error = on_token_lookup_error
        self.on_token_decoding_error = on_token_decoding_error

    async def __call__(self, request: Request) -> JWTClaims:
        try:
            credentials = await super().__call__(request)
        except HTTPException:
            raise self.on_token_lookup_error()

        try:
            decoded = self.token_decoder.decode(credentials.credentials)
        except exceptions.AuthorizationError:
            raise self.on_token_decoding_error()

        return decoded


class JWTCookieAuth:
    def __init__(
        self,
        key: str,
        token_decoder: JWTDecoder,
        on_token_lookup_error: Callable[[], HTTPException],
        on_token_decoding_error: Callable[[], HTTPException],
    ):
        self.key = key
        self.token_decoder = token_decoder
        self.on_token_lookup_error = on_token_lookup_error
        self.on_token_decoding_error = on_token_decoding_error

    async def __call__(self, request: Request) -> JWTClaims:
        if (credentials := request.cookies.get(self.key)) is None:
            raise self.on_token_lookup_error()

        try:
            decoded = self.token_decoder.decode(credentials)
        except exceptions.AuthorizationError:
            raise self.on_token_decoding_error()

        return decoded

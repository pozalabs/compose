import http
import secrets
from collections.abc import Callable
from typing import Annotated, Self

from authlib.jose import JWTClaims
from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyHeader, HTTPBasic, HTTPBasicCredentials, HTTPBearer

from compose import exceptions
from compose.auth import JWTDecoder


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


class APIKeyAuth:
    """API Key Authentication for FastAPI

    Example:
    ```python
    import compose
    from fastapi import Depends
    from fastapi.security import APIKeyHeader

    app = FastAPI()
    api_key_header = APIKeyHeader("x-api-key", auto_error=False)

    # 고정 API Key 인증
    api_key_auth = compose.fastapi.APIKeyAuth.static(
        api_key="api-key",
        header=api_key_header,
    ).authenticator()

    # 동적 API Key 인증
    api_key_auth = compose.fastapi.APIKeyAuth(
        api_key_factory=api_key_factory,
        header=api_key_header,
    ).authenticator()

    @app.get("/auth/api-key", dependencies=[Depends(api_key_auth)])
    def authed_by_api_key():
        return {"message": "Authenticated"}
    """

    def __init__(self, api_key_factory: Callable[[], str], header: APIKeyHeader):
        self.api_key_factory = api_key_factory
        self.header = header

    def authenticator(self) -> Callable[[str], None]:
        _header = self.header

        def authenticate(header: Annotated[str, Depends(_header)]) -> None:
            api_key = self.api_key_factory()
            if header != api_key:
                raise HTTPException(
                    status_code=http.HTTPStatus.UNAUTHORIZED,
                    detail="Not authenticated. Invalid API key",
                )

        return authenticate

    @classmethod
    def static(cls, api_key: str, header: APIKeyHeader) -> Self:
        return cls(api_key_factory=lambda: api_key, header=header)


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

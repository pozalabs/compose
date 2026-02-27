from collections.abc import Callable
from typing import ClassVar, Self

from authlib.integrations.httpx_client import AsyncOAuth2Client

from . import vo


class AuthorizationServer:
    headers: ClassVar[dict[str, str]] = {"Content-Type": "application/x-www-form-urlencoded"}

    def __init__(
        self,
        auth_client_factory: Callable[..., AsyncOAuth2Client],
        access_token_url: str,
    ):
        self.auth_client_factory = auth_client_factory
        self.access_token_url = access_token_url

    @classmethod
    def default(cls, client_id: str, client_secret: str, access_token_url: str) -> Self:
        return cls(
            auth_client_factory=lambda: AsyncOAuth2Client(
                client_id=client_id,
                client_secret=client_secret,
            ),
            access_token_url=access_token_url,
        )

    async def grant_authorization(self, redirect_uri: str, code: str) -> vo.AuthorizationGrant:
        async with self.auth_client_factory() as client:
            response = await client.fetch_token(
                url=self.access_token_url,
                headers=self.headers,
                grant_type="authorization_code",
                client_id=client.client_id,
                client_secret=client.client_secret,
                redirect_uri=redirect_uri,
                code=code,
            )
        return vo.AuthorizationGrant.model_validate(response)

    async def renew_token(self, token: str) -> vo.AuthorizationGrant:
        async with self.auth_client_factory() as client:
            response = await client.fetch_token(
                url=self.access_token_url,
                headers=self.headers,
                grant_type="refresh_token",
                client_id=client.client_id,
                client_secret=client.client_secret,
                refresh_token=token,
            )
        return vo.AuthorizationGrant.model_validate(response)

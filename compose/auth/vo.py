from typing import Any

from pydantic import Field

from .. import container


class AuthorizationGrant(container.BaseModel):
    access_token: str
    refresh_token: str | None = None


class UserResource(container.BaseModel):
    email: str
    name: str


class TokenClaims(container.BaseModel):
    sub: str
    iss: str
    jti: str
    iat: int
    exp: int
    extra: dict[str, Any] = Field(default_factory=dict)

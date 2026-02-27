from typing import Any

from .. import container


class TokenClaims(container.BaseModel):
    sub: str
    iss: str
    jti: str
    iat: int
    exp: int
    extra: dict[str, Any] = {}

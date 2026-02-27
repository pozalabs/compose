from typing import Self

import pendulum
from authlib.jose import errors, jwt

from .. import exceptions
from . import vo

_STANDARD_CLAIM_KEYS = frozenset({"sub", "iss", "jti", "iat", "exp"})


class JWTDecoder:
    def __init__(self, secret_key: str, clock: type[pendulum.DateTime]):
        self.secret_key = secret_key
        self.clock = clock

    @classmethod
    def default(cls, secret_key: str) -> Self:
        return cls(secret_key=secret_key, clock=pendulum.DateTime)

    def decode(self, token: str) -> vo.TokenClaims:
        try:
            decoded = jwt.decode(token.encode(), key=self.secret_key)
        except (errors.DecodeError, errors.BadSignatureError):
            raise exceptions.AuthorizationError("Invalid token")

        try:
            decoded.validate(now=int(self.clock.utcnow().timestamp()))
        except errors.ExpiredTokenError:
            raise exceptions.AuthorizationError("Token has expired")
        except errors.InvalidClaimError:
            raise exceptions.AuthorizationError("Expired or incorrect format")

        extra = {k: v for k, v in decoded.items() if k not in _STANDARD_CLAIM_KEYS}
        return vo.TokenClaims(
            sub=decoded["sub"],
            iss=decoded["iss"],
            jti=decoded["jti"],
            iat=decoded["iat"],
            exp=decoded["exp"],
            extra=extra,
        )

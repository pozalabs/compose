from typing import Self

import pendulum
from joserfc import errors, jwk, jwt

from .. import exceptions
from . import vo

_STANDARD_CLAIM_KEYS = frozenset({"sub", "iss", "jti", "iat", "exp"})


class JWTDecoder:
    def __init__(self, secret_key: str, clock: type[pendulum.DateTime]):
        self.secret_key = jwk.OctKey.import_key(secret_key)
        self.clock = clock

    @classmethod
    def default(cls, secret_key: str) -> Self:
        return cls(secret_key=secret_key, clock=pendulum.DateTime)

    def decode(self, token: str) -> vo.TokenClaims:
        try:
            decoded = jwt.decode(token, key=self.secret_key)
        except (errors.DecodeError, errors.BadSignatureError):
            raise exceptions.AuthorizationError("Invalid token")

        claim_requests = jwt.JWTClaimsRegistry(now=int(self.clock.utcnow().timestamp()))
        claims = decoded.claims
        try:
            claim_requests.validate(claims)
        except errors.ClaimError as exc:
            raise exceptions.AuthorizationError(exc.description) from exc

        extra = {k: v for k, v in claims.items() if k not in _STANDARD_CLAIM_KEYS}
        return vo.TokenClaims(
            sub=claims["sub"],
            iss=claims["iss"],
            jti=claims["jti"],
            iat=claims["iat"],
            exp=claims["exp"],
            extra=extra,
        )

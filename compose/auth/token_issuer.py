from collections.abc import Callable

import pendulum
from authlib.jose import jwt


class JWTIssuer:
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        issuer: str,
        token_id_generator: Callable[[], str],
        clock: Callable[..., pendulum.DateTime],
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.issuer = issuer
        self.token_id_generator = token_id_generator
        self.clock = clock

    def issue(self, sub: str, expires_in: int, **kwargs) -> str:
        iat = self.clock.utcnow()
        return jwt.encode(
            header={"typ": "JWT", "alg": self.algorithm},
            payload={
                "sub": sub,
                "iss": self.issuer,
                "jti": self.token_id_generator(),
                "iat": int(iat.timestamp()),
                "exp": int(iat.add(seconds=expires_in).timestamp()),
                **kwargs,
            },
            key=self.secret_key,
        ).decode()

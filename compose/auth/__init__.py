from .resource_server import ResourceServer
from .vo import AuthorizationGrant, TokenClaims, UserResource

__all__ = [
    "AuthorizationGrant",
    "ResourceServer",
    "TokenClaims",
    "UserResource",
]

try:
    from .authorization_server import AuthorizationServer
    from .token_decoder import JWTDecoder
    from .token_issuer import JWTIssuer

    __all__ += ["AuthorizationServer", "JWTDecoder", "JWTIssuer"]
except ImportError:
    pass

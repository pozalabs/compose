from .resource_server import ResourceServer
from .vo import AuthorizationGrant, TokenClaims, UserResource

__all__ = [
    "AuthorizationGrant",
    "ResourceServer",
    "TokenClaims",
    "UserResource",
]

try:
    from .token_decoder import JWTDecoder
    from .token_issuer import JWTIssuer

    __all__ += ["JWTDecoder", "JWTIssuer"]
except ImportError:
    pass

try:
    from .authorization_server import AuthorizationServer

    __all__ += ["AuthorizationServer"]
except ImportError:
    pass

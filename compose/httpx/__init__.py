from .._internal import is_package_installed

if not is_package_installed("httpx"):
    raise ImportError("Install `httpx` extra to use httpx features")

from .auth.api_key import HeaderAPIKeyAuth

__all__ = ["HeaderAPIKeyAuth"]

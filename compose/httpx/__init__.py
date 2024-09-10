try:
    import httpx  # noqa: F401
except ImportError:
    raise ImportError("Install `httpx` extra to use httpx features")

from .auth.api_key import HeaderAPIKeyAuth

__all__ = ["HeaderAPIKeyAuth"]

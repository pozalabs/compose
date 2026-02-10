try:
    from .auth.header import HeaderAuth
except ImportError:
    raise ImportError("Install `httpx` extra to use httpx features") from None

__all__ = ["HeaderAuth"]

try:
    import opentelemetry  # noqa: F401
except ImportError:
    raise ImportError("Install `opentelemetry` extra to use opentelemetry features")

from .instrumentation.loguru.instrumentor import LoguruInstrumentor

__all__ = ["LoguruInstrumentor"]

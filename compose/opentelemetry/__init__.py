try:
    import opentelemetry  # noqa: F401
except ImportError:
    raise ImportError("Install `opentelemetry` extra to use opentelemetry features")

from .instrumentation.loguru.instrumentor import LoguruInstrumentor
from .tracer_provider import get_default_tracer_provider

__all__ = ["LoguruInstrumentor", "get_default_tracer_provider"]

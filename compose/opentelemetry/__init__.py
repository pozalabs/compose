try:
    from .instrumentation.loguru.instrumentor import LoguruInstrumentor
    from .tracer_provider import get_default_tracer_provider
except ImportError:
    raise ImportError("Install `opentelemetry` extra to use opentelemetry features") from None

__all__ = ["LoguruInstrumentor", "get_default_tracer_provider"]

try:
    from .instrumentation.loguru.instrumentor import LoguruInstrumentor
    from .meter_provider import get_default_meter_provider
    from .tracer_provider import ServiceResourceAttrs, get_default_tracer_provider
except ImportError:
    raise ImportError("Install the 'otel' extra to use otel features") from None

__all__ = [
    "LoguruInstrumentor",
    "ServiceResourceAttrs",
    "get_default_meter_provider",
    "get_default_tracer_provider",
]

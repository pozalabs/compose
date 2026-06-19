try:
    from .instrumentation.loguru.instrumentor import LoguruInstrumentor
    from .tracer_provider import ServiceResourceAttrs, get_default_tracer_provider
except ImportError:
    raise ImportError(
        "Install opentelemetry-api, opentelemetry-sdk,"
        " and opentelemetry-exporter-otlp-proto-http to use otel features"
    ) from None

__all__ = ["LoguruInstrumentor", "ServiceResourceAttrs", "get_default_tracer_provider"]

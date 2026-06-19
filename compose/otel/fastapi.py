from typing import TYPE_CHECKING

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import Sampler

from .instrumentation.loguru.instrumentor import LoguruInstrumentor
from .meter_provider import get_default_meter_provider
from .tracer_provider import ServiceResourceAttrs, get_default_tracer_provider

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
except ImportError:
    raise ImportError(
        "Install `opentelemetry-instrumentation-fastapi` to use `compose.otel.fastapi`"
    ) from None

if TYPE_CHECKING:
    from fastapi import FastAPI


DEFAULT_OTLP_ENDPOINT = "http://localhost:4318"


def instrument_app(
    app: FastAPI,
    resource_attrs: ServiceResourceAttrs,
    otlp_endpoint: str = DEFAULT_OTLP_ENDPOINT,
    sampler: Sampler | None = None,
    tracer_provider: TracerProvider | None = None,
    meter_provider: MeterProvider | None = None,
) -> None:
    from compose.fastapi.otel import NonInstrumentedUrls

    if tracer_provider is None:
        tracer_provider = get_default_tracer_provider(
            resource_attrs=resource_attrs,
            exporter_endpoint=f"{otlp_endpoint}/v1/traces",
            sampler=sampler,
        )
    trace.set_tracer_provider(tracer_provider)

    if meter_provider is None:
        meter_provider = get_default_meter_provider(
            resource_attrs=resource_attrs,
            exporter_endpoint=f"{otlp_endpoint}/v1/metrics",
        )
    metrics.set_meter_provider(meter_provider)

    FastAPIInstrumentor.instrument_app(
        app=app,
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
        excluded_urls=",".join(NonInstrumentedUrls.current()),
    )
    LoguruInstrumentor().instrument()  # type: ignore[misc]

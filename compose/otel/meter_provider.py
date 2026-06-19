from collections.abc import Sequence

from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import View
from opentelemetry.sdk.resources import Resource

from ..types import MilliSeconds
from .tracer_provider import ServiceResourceAttrs


def get_default_meter_provider(
    resource_attrs: ServiceResourceAttrs,
    exporter_endpoint: str,
    export_interval: MilliSeconds | None = None,
    export_timeout: MilliSeconds | None = None,
    views: Sequence[View] = (),
) -> MeterProvider:
    reader_kwargs: dict = {}
    if export_interval is not None:
        reader_kwargs["export_interval_millis"] = export_interval
    if export_timeout is not None:
        reader_kwargs["export_timeout_millis"] = export_timeout

    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=exporter_endpoint),
        **reader_kwargs,
    )
    return MeterProvider(
        resource=Resource.create(resource_attrs.to_attrs()),
        metric_readers=[reader],
        views=views,
    )

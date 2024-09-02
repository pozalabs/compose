from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Attributes, LabelValue, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


class ServiceResourceAttrs:
    def __init__(
        self,
        name: str,
        version: str,
        environment: str,
        **extra: LabelValue,
    ):
        self._attrs = {
            "name": name,
            "version": version,
            "environment": environment,
            **extra,
        }

    def to_attrs(self) -> Attributes:
        return {f"service.{key}": value for key, value in self._attrs.items()}


def get_default_tracer_provider(
    resource_attrs: ServiceResourceAttrs,
    exporter_endpoint: str,
) -> TracerProvider:
    tracer_provider = TracerProvider(resource=Resource.create(resource_attrs.to_attrs()))
    exporter = OTLPSpanExporter(endpoint=exporter_endpoint)
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    return tracer_provider

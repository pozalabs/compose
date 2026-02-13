from __future__ import annotations

from collections.abc import Callable, Collection
from typing import TYPE_CHECKING

import wrapt
from loguru import logger
from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap

ORIGINAL_PATCHER_ATTR = "_otel_original_patcher"
_instruments = tuple()

if TYPE_CHECKING:
    from loguru import Logger, Record


RecordPatcher = Callable[["Record"], None]


def create_trace_patcher(tracer_provider: trace.TracerProvider) -> RecordPatcher:
    resource = getattr(tracer_provider, "resource", None)
    service_name = resource.attributes.get("service.name", "") if resource is not None else ""

    def patcher(record: Record) -> None:
        span = trace.get_current_span()
        ctx = span.get_span_context()
        is_valid_span = span != trace.INVALID_SPAN

        record["extra"].update(
            {
                "otel_service_name": service_name,
                "otel_trace_id": (
                    trace.format_trace_id(ctx.trace_id)
                    if is_valid_span
                    else str(trace.INVALID_TRACE_ID)
                ),
                "otel_span_id": (
                    trace.format_span_id(ctx.span_id)
                    if is_valid_span
                    else str(trace.INVALID_SPAN_ID)
                ),
                "otel_trace_sampled": ctx.trace_flags.sampled if is_valid_span else False,
            }
        )

    return patcher


def create_configure_wrapper(
    trace_patcher: RecordPatcher,
) -> Callable[..., list[int]]:
    def wrapped_configure(
        func: Callable[..., list[int]],
        instance: Logger,
        args: tuple,
        kwargs: dict,
    ) -> list[int]:
        original_patcher = kwargs.get("patcher")
        setattr(instance, ORIGINAL_PATCHER_ATTR, original_patcher)

        if original_patcher is None:
            return func(*args, **kwargs)

        user_patcher: RecordPatcher = original_patcher

        def wrapped_patcher(record: Record) -> None:
            user_patcher(record)
            trace_patcher(record)

        kwargs["patcher"] = wrapped_patcher
        return func(*args, **kwargs)

    return wrapped_configure


def _default_record_patcher(_: Record) -> None:
    return None


class LoguruInstrumentor(BaseInstrumentor):
    """
    Reference:
        https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-logging
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs) -> None:
        tracer_provider = kwargs.get("tracer_provider", trace.get_tracer_provider())

        trace_patcher = create_trace_patcher(tracer_provider)
        logger.configure(patcher=trace_patcher)
        wrapt.wrap_function_wrapper(
            logger,
            "configure",
            create_configure_wrapper(trace_patcher),
        )

    def _uninstrument(self, **kwargs) -> None:
        original_patcher = getattr(logger, ORIGINAL_PATCHER_ATTR, None)
        unwrap(logger, "configure")
        logger.configure(patcher=original_patcher or _default_record_patcher)
        if hasattr(logger, ORIGINAL_PATCHER_ATTR):
            delattr(logger, ORIGINAL_PATCHER_ATTR)

import logging
from collections.abc import Generator

import pytest
from _pytest.logging import LogCaptureFixture
from loguru import logger
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.test.globals_test import reset_trace_globals

from compose.opentelemetry import LoguruInstrumentor


@pytest.fixture
def caplog(caplog: LogCaptureFixture) -> Generator[LogCaptureFixture, None, None]:
    """
    Reference:
        https://loguru.readthedocs.io/en/stable/resources/migration.html#replacing-caplog-fixture-from-pytest-library
    """

    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level=0,
        filter=lambda record: record["level"].no >= caplog.handler.level,
        enqueue=False,
    )
    yield caplog
    logger.remove(handler_id)


@pytest.fixture
def tracer_provider() -> Generator[TracerProvider, None, None]:
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(InMemorySpanExporter()))
    reset_trace_globals()
    trace.set_tracer_provider(provider)
    yield provider
    reset_trace_globals()


@pytest.fixture
def instrumentor(tracer_provider: TracerProvider) -> Generator[LoguruInstrumentor, None, None]:
    inst = LoguruInstrumentor()
    inst.instrument(tracer_provider=tracer_provider)
    yield inst
    inst.uninstrument()


@pytest.fixture
def tracer() -> trace.Tracer:
    return trace.get_tracer(__name__)


def test_inject_trace_context(
    instrumentor: LoguruInstrumentor,
    tracer: trace.Tracer,
    caplog: LogCaptureFixture,
):
    with tracer.start_as_current_span("span1") as span:
        with caplog.at_level(logging.INFO):
            ctx = span.get_span_context()

            logger.info("Hello")
            extra = caplog.records[0].extra  # type: ignore[missing-attribute]

            assert extra == {
                "otel_service_name": "unknown_service",
                "otel_span_id": trace.format_span_id(ctx.span_id),
                "otel_trace_id": trace.format_trace_id(ctx.trace_id),
                "otel_trace_sampled": ctx.trace_flags.sampled,
            }


def test_inject_invalid_trace_context_outside_span(
    instrumentor: LoguruInstrumentor,
    caplog: LogCaptureFixture,
):
    with caplog.at_level(logging.INFO):
        logger.info("Hello")
        extra = caplog.records[0].extra  # type: ignore[missing-attribute]

        assert extra["otel_trace_id"] == str(trace.INVALID_TRACE_ID)
        assert extra["otel_span_id"] == str(trace.INVALID_SPAN_ID)
        assert extra["otel_trace_sampled"] is False


def test_uninstrument(
    instrumentor: LoguruInstrumentor,
    tracer: trace.Tracer,
    caplog: LogCaptureFixture,
):
    instrumentor.uninstrument()
    with tracer.start_as_current_span("span1"):
        with caplog.at_level(logging.INFO):
            logger.info("Hello")
            assert not caplog.records[0].extra  # type: ignore[missing-attribute]


def test_preserve_user_patcher_after_uninstrument(
    tracer_provider: TracerProvider,
    caplog: LogCaptureFixture,
):
    marker = {"patched": True}

    def user_patcher(record):
        record["extra"].update(marker)

    logger.configure(patcher=user_patcher)

    instrumentor = LoguruInstrumentor()
    instrumentor.instrument(tracer_provider=tracer_provider)
    logger.configure(patcher=user_patcher)
    instrumentor.uninstrument()

    with caplog.at_level(logging.INFO):
        logger.info("Hello")
        assert caplog.records[0].extra == marker  # type: ignore[missing-attribute]

    logger.configure(patcher=lambda r: None)


def test_chain_user_patcher_with_trace_injection(
    tracer_provider: TracerProvider,
    tracer: trace.Tracer,
    caplog: LogCaptureFixture,
):
    def user_patcher(record):
        record["extra"]["custom"] = "value"

    logger.configure(patcher=user_patcher)

    instrumentor = LoguruInstrumentor()
    instrumentor.instrument(tracer_provider=tracer_provider)
    logger.configure(patcher=user_patcher)

    with tracer.start_as_current_span("span1") as span:
        with caplog.at_level(logging.INFO):
            ctx = span.get_span_context()
            logger.info("Hello")
            extra = caplog.records[0].extra  # type: ignore[missing-attribute]

            assert extra["custom"] == "value"
            assert extra["otel_trace_id"] == trace.format_trace_id(ctx.trace_id)

    instrumentor.uninstrument()
    logger.configure(patcher=lambda r: None)

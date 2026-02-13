import logging
from collections.abc import Generator

import pytest
from _pytest.logging import LogCaptureFixture
from loguru import logger
from opentelemetry import trace
from opentelemetry.test.test_base import TestBase

import compose


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


class TestLoguruInstrumentor(TestBase):
    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog: LogCaptureFixture):
        self.caplog = caplog

    def setUp(self):
        super().setUp()
        self.instrumentor = compose.opentelemetry.LoguruInstrumentor()
        self.instrumentor.instrument()
        self.tracer = trace.get_tracer(__name__)

    def tearDown(self):
        super().tearDown()
        self.instrumentor.uninstrument()

    def test_trace_context_injection(self):
        with self.tracer.start_as_current_span("span1") as span:
            with self.caplog.at_level(logging.INFO):
                ctx = span.get_span_context()

                logger.info("Hello")
                record = self.caplog.records[0]
                extra = record.extra

                expected_trace_context = {
                    "otel_service_name": "unknown_service",
                    "otel_span_id": trace.format_span_id(ctx.span_id),
                    "otel_trace_id": trace.format_trace_id(ctx.trace_id),
                    "otel_trace_sampled": ctx.trace_flags.sampled,
                }

                assert extra == expected_trace_context

    def test_inject_invalid_trace_context_outside_span(self):
        with self.caplog.at_level(logging.INFO):
            logger.info("Hello")
            record = self.caplog.records[0]
            extra = record.extra

            assert extra["otel_trace_id"] == str(trace.INVALID_TRACE_ID)
            assert extra["otel_span_id"] == str(trace.INVALID_SPAN_ID)
            assert extra["otel_trace_sampled"] is False

    def test_uninstrument(self):
        self.instrumentor.uninstrument()
        with self.tracer.start_as_current_span("span1"):
            with self.caplog.at_level(logging.INFO):
                logger.info("Hello")

                record = self.caplog.records[0]
                extra = record.extra

                assert not extra

    def test_preserve_user_patcher_after_uninstrument(self):
        self.instrumentor.uninstrument()

        marker = {"patched": True}

        def user_patcher(record):
            record["extra"].update(marker)

        logger.configure(patcher=user_patcher)
        self.instrumentor.instrument()
        logger.configure(patcher=user_patcher)
        self.instrumentor.uninstrument()

        with self.caplog.at_level(logging.INFO):
            logger.info("Hello")
            record = self.caplog.records[0]

            assert record.extra == marker

        logger.configure(patcher=lambda r: None)

    def test_chain_user_patcher_with_trace_injection(self):
        self.instrumentor.uninstrument()

        def user_patcher(record):
            record["extra"]["custom"] = "value"

        logger.configure(patcher=user_patcher)
        self.instrumentor.instrument()
        logger.configure(patcher=user_patcher)

        with self.tracer.start_as_current_span("span1") as span:
            with self.caplog.at_level(logging.INFO):
                ctx = span.get_span_context()
                logger.info("Hello")
                record = self.caplog.records[0]
                extra = record.extra

                assert extra["custom"] == "value"
                assert extra["otel_trace_id"] == trace.format_trace_id(ctx.trace_id)

        logger.configure(patcher=lambda r: None)

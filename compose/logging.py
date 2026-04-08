from __future__ import annotations

import dataclasses
import enum
import logging
import os
import sys
from collections.abc import Iterable
from types import FrameType
from typing import TYPE_CHECKING, Protocol, Self, Unpack

try:
    from loguru import logger
except ImportError:
    raise ImportError("Install `loguru` extra to use logging features") from None

if TYPE_CHECKING:
    from loguru import BasicHandlerConfig, Logger, Record


class InterceptHandler(logging.Handler):
    """표준 logging으로 발생한 로그를 loguru로 전달하는 브릿지 핸들러.

    gunicorn, uvicorn처럼 자체 핸들러를 등록하는 라이브러리는 root 로거의 loguru 설정이
    덮어써지므로, 해당 로거의 핸들러를 직접 교체하여 loguru 파이프라인으로 통합함.

    https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        # 콜스택을 역추적하여 실제 로그 호출 지점의 depth를 계산함.
        # loguru가 InterceptHandler 내부가 아닌 원래 로그 발생 위치를 기록하기 위함.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame: FrameType | None = logging.currentframe()
        depth = 0
        while frame is not None and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def route_to_loguru(
    intercept_handler: InterceptHandler,
    logger_names: Iterable[str] = (
        "gunicorn.error",
        "gunicorn.access",
        "uvicorn.error",
        "uvicorn.access",
    ),
) -> None:
    logging.basicConfig(handlers=[intercept_handler], level=logging.INFO, force=True)
    for name in logger_names:
        lg = logging.getLogger(name)
        lg.handlers = [intercept_handler]
        lg.propagate = False


class LogFilterOp(Protocol):
    def __call__(self, record: Record) -> bool: ...


class LogFilterNotContains:
    def __init__(self, pattern: str):
        self.pattern = pattern

    def __call__(self, record: Record) -> bool:
        return self.pattern not in record["message"]


class LogFilter:
    def __init__(self, *ops: *tuple[LogFilterOp, ...]):
        self.ops = list(ops)

    def __call__(self, record: Record) -> bool:
        return all(op(record) for op in self.ops)


class LogFormat(enum.StrEnum):
    SERIALIZED = "{message}"
    NON_SERIALIZED = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | <level>{level: <8}</level> | <level>{message}</level>"
    )


@dataclasses.dataclass
class LogDisplayConfig:
    format: str
    colorize: bool
    serialize: bool

    @classmethod
    def serialized(cls) -> Self:
        return cls(
            format=LogFormat.SERIALIZED,
            colorize=False,
            serialize=True,
        )

    @classmethod
    def non_serialized(cls) -> Self:
        return cls(
            format=LogFormat.NON_SERIALIZED,
            colorize=True,
            serialize=False,
        )


def create_logger(serialize: bool = False, **config: Unpack[BasicHandlerConfig]) -> Logger:  # type: ignore[bad-function-definition]
    display = LogDisplayConfig.serialized() if serialize else LogDisplayConfig.non_serialized()
    level = config.get("level", logging.INFO)

    intercept_handler = InterceptHandler()
    logging.basicConfig(handlers=[intercept_handler], level=level, force=True)
    route_to_loguru(intercept_handler=intercept_handler)

    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": level,
                "diagnose": False,
                "filter": LogFilter(
                    LogFilterNotContains("/health-check"),
                    LogFilterNotContains("/metrics"),
                ),
                **dataclasses.asdict(display),
            }
            | config
        ]
    )

    return logger


class LogLevel(int):
    @classmethod
    def from_env(cls, env: str) -> Self:
        return cls(os.getenv(env, logging.INFO))

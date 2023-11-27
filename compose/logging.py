import logging

try:
    from loguru import logger
except ImportError:
    raise ImportError(
        "The `loguru` extra must be installed to use the `compose.logging` module. "
        "Install `compose` with `loguru` extra (`compose[loguru]`)"
    )


class InterceptHandler(logging.Handler):
    """https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging"""  # noqa: E501

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    def filter(self, record: logging.LogRecord) -> bool:
        return "/health-check" not in record.getMessage()


def intercept_logging(log_level: int) -> None:
    """Python 내장 logging 모듈을 loguru로 대체합니다. (해당 함수를 호출하려면 `loguru`를 설치해야 합니다.)

    ```python
    import compose

    compose.logging.intercept_logging(logging.INFO)
    ```
    """
    logging.basicConfig(handlers=[InterceptHandler()], level=log_level, force=True)

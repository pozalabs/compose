import compose
from src import LOG_LEVEL
from src.settings import settings

logger = compose.logging.get_default_logger(
    log_level=LOG_LEVEL,
    serialize_log=settings.serialize_log,
)

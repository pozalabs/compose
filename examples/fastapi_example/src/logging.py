import compose
from src import LOG_LEVEL
from src.settings import settings

logger = compose.logging.create_logger(
    level=LOG_LEVEL,
    serialize=settings.serialize_log,
)

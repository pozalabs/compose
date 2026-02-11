import logging
import os

import compose

APP_ENV = compose.enums.AppEnv.current()
LOG_LEVEL = os.getenv("LOG_LEVEL", logging.INFO)

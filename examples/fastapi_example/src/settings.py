from pydantic.v1 import BaseSettings, Extra

import compose
from src import APP_ENV


class Settings(BaseSettings):
    class Config:
        extra = Extra.ignore

    @property
    def serialize_log(self) -> bool:
        return APP_ENV not in (compose.enums.AppEnv.LOCAL, compose.enums.AppEnv.TEST)


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict

import compose
from src import APP_ENV


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    @property
    def serialize_log(self) -> bool:
        return APP_ENV not in (compose.enums.AppEnv.LOCAL, compose.enums.AppEnv.TEST)


settings = Settings()

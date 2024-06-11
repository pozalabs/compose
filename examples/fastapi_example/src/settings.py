from pydantic.v1.env_settings import BaseSettings, Extra

# v2
# from pydantic_settings import BaseSettings, SettingsConfigDict
import compose
from src import APP_ENV


class Settings(BaseSettings):
    class Config:
        extra = Extra.ignore

    # v2
    # model_config = SettingsConfigDict(extra="ignore")

    @property
    def serialize_log(self) -> bool:
        return APP_ENV not in (compose.enums.AppEnv.LOCAL, compose.enums.AppEnv.TEST)


settings = Settings()

# 예제는 compose 개발 의존성을 그대로 사용하기 때문에 불가피하게 `pydantic.v1.env_settings`를 사용하였습니다.
# `compose`를 사용하는 어플리케이션에서는 `pydantic_settings`를 사용하세요.
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

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    app_name: str = Field("Order Service", alias="APP_NAME")
    environment: Literal["local", "dev", "development", "prod", "test"] = Field(
        "dev", alias="ENVIRONMENT"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        "INFO", alias="LOG_LEVEL"
    )
    debug: bool = Field(False, alias="DEBUG")
    rate_limit_per_minute: int = Field(30, alias="RATE_LIMIT_PER_MINUTE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

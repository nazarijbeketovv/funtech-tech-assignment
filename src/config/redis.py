"""Настройки Redis (кеш и инфраструктурные параметры)."""

from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    """Настройки подключения к Redis и параметров кеширования."""

    redis_url: RedisDsn = Field(
        RedisDsn("redis://:redis_password@redis:6379/0"), alias="REDIS_URL"
    )
    redis_password: str = Field("redis_password", alias="REDIS_PASSWORD")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    redis_host: str = Field("redis", alias="REDIS_HOST")
    redis_db: int = Field(0, alias="REDIS_DB")
    redis_cache_ttl: int = Field(300, alias="REDIS_CACHE_TTL")
    redis_cache_prefix: str = Field("order_service:", alias="REDIS_CACHE_PREFIX")

    class Config:
        """Настройки загрузки переменных окружения для Pydantic Settings."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

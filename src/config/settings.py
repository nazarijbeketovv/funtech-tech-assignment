"""Сборная конфигурация приложения (Settings).

`Settings` агрегирует настройки разных подсистем в один объект и предоставляет
удобные свойства (например, `database_url`, `redis_url`).
"""

from pydantic_settings import BaseSettings

from config.app import AppSettings
from config.auth import AuthSettings
from config.broker import BrokerSettings
from config.cors import CORSSettings
from config.database import DatabaseSettings
from config.redis import RedisSettings


class Settings(BaseSettings):
    """Корневые настройки приложения."""

    app: AppSettings = AppSettings()
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    broker: BrokerSettings = BrokerSettings()
    cors: CORSSettings = CORSSettings()
    auth: AuthSettings = AuthSettings()

    @property
    def app_name(self) -> str:
        """Название приложения (для документации/логов)."""
        return self.app.app_name

    @property
    def environment(self) -> str:
        """Текущее окружение (dev/prod/test и т.п.)."""
        return self.app.environment

    @property
    def log_level(self) -> str:
        """Уровень логирования."""
        return self.app.log_level

    @property
    def debug(self) -> bool:
        """Флаг режима отладки."""
        return self.app.debug

    @property
    def database_url(self) -> str:
        """URL подключения к БД (asyncpg)."""
        return str(self.database.database_url)

    @property
    def sqlalchemy_database_uri(self) -> str:
        """URI SQLAlchemy (для совместимости/инструментов)."""
        return str(self.database.sqlalchemy_database_uri)

    @property
    def redis_url(self) -> str:
        """URL подключения к Redis."""
        return str(self.redis.redis_url)

    class Config:
        """Настройки загрузки переменных окружения для Pydantic Settings."""

        env_file = ".env"
        env_nested_delimiter = "__"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

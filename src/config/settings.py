from pydantic_settings import BaseSettings

from config.app import AppSettings
from config.auth import AuthSettings
from config.broker import BrokerSettings
from config.cors import CORSSettings
from config.database import DatabaseSettings
from config.redis import RedisSettings


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    broker: BrokerSettings = BrokerSettings()
    cors: CORSSettings = CORSSettings()
    auth: AuthSettings = AuthSettings()

    @property
    def app_name(self) -> str:
        return self.app.app_name

    @property
    def environment(self) -> str:
        return self.app.environment

    @property
    def log_level(self) -> str:
        return self.app.log_level

    @property
    def debug(self) -> bool:
        return self.app.debug

    @property
    def database_url(self) -> str:
        return str(self.database.database_url)

    @property
    def sqlalchemy_database_uri(self) -> str:
        return str(self.database.sqlalchemy_database_uri)

    @property
    def redis_url(self) -> str:
        return str(self.redis.redis_url)

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

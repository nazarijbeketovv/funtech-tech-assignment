"""Настройки брокера сообщений (RabbitMQ)."""

from pydantic import Field
from pydantic_settings import BaseSettings


class BrokerSettings(BaseSettings):
    """Настройки подключения и публикации событий в брокер."""

    broker_url: str = Field(..., alias="BROKER_URL")
    broker_new_order_queue: str = Field(
        "new_order", alias="BROKER_NEW_ORDER_QUEUE"
    )
    publish_retries: int = Field(3, alias="PUBLISH_RETRIES")
    publish_retry_backoff: float = Field(0.5, alias="PUBLISH_RETRY_BACKOFF")

    class Config:
        """Настройки загрузки переменных окружения для Pydantic Settings."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

"""Конфигурация приложения.

Пакет содержит модели настроек (Pydantic BaseSettings), сгруппированные по
подсистемам: приложение, БД, Redis, брокер сообщений, CORS и аутентификация.
"""

from config.settings import Settings

__all__ = ["Settings"]

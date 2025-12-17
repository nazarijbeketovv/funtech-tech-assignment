"""Совместимость: прокси для новой loguru-конфигурации."""

from infra.logger.setup import setup_logging as setup_loguru_logging


def setup_logging(log_level: str = "INFO") -> None:
    """Поддержка старого импорта, перенаправляет на loguru-setup."""
    setup_loguru_logging()

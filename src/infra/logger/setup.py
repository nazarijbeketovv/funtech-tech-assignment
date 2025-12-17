"""Модуль инициализации и настройки системы логирования."""

import logging

from infra.logger.configure.interceptor import InterceptHandler
from infra.logger.configure.sinks import configure_sinks


def setup_logging() -> None:
    """Настройка логирования приложения.

    Перехватывает стандартные логгеры и перенаправляет их в loguru.
    Метод вызывается в точке входа.
    """
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.NOTSET)
    logging.captureWarnings(True)

    loggers = (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "starlette",
    )
    for log_name in loggers:
        logger_instance = logging.getLogger(log_name)
        logger_instance.handlers = [InterceptHandler()]
        logger_instance.propagate = False

    configure_sinks()

"""Модуль перехватчика логов для интеграции с различными системами логирования."""

import inspect
import logging

from loguru import logger

from infra.logger.context import trace_id_var


class InterceptHandler(logging.Handler):
    """Обработчик перехваченных логов"""

    def emit(self, record: logging.LogRecord) -> None:
        """Перехватывает логи из стандартного модуля logging и перенаправляет в Loguru.

        Args:
            record: Запись лога из стандартного модуля logging
        """
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen = "importlib" in filename and "_bootstrap" in filename
            if depth > 0 and not (is_logging or is_frozen):
                break
            frame = frame.f_back
            depth += 1

        trace_id = trace_id_var.get()

        message = record.getMessage()
        logger_instance = logger.opt(depth=depth, exception=record.exc_info)
        logger_instance.bind(trace_id=trace_id).log(level, message)

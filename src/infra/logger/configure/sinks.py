"""Модуль настройки приемников (sinks) для логов."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from loguru import logger

from config.settings import settings
from infra.logger.context import trace_id_var


if TYPE_CHECKING:
    from loguru import Record
DEFAULT_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | "
    "trace_id={extra[trace_id]} | {message}"
)


def _patch_record(record: Record) -> None:
    """Добавляет trace_id в каждую лог-запись перед отправкой в sink."""
    record["extra"]["trace_id"] = trace_id_var.get()


def configure_sinks() -> None:
    """Настройка обработчиков логов."""
    logger.remove()
    logger.configure(patcher=_patch_record)

    if settings.environment == "test":
        return

    logger.add(
        sys.stderr,
        level=settings.log_level,
        diagnose=False,
        backtrace=False,
        enqueue=True,
        serialize=not settings.debug,
        format=DEFAULT_FORMAT,
    )

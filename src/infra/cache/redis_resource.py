"""Глобальный ресурс Redis-клиента для lifespan.

Модуль хранит ссылку на Redis-клиент, инициализируемый в `main.lifespan`,
чтобы инфраструктурные компоненты могли получать доступ к нему без передачи по
цепочке зависимостей.
"""

from __future__ import annotations

import redis.asyncio as redis

_redis_client: redis.Redis | None = None  # type: ignore[type-arg]


def set_redis_client(client: redis.Redis) -> None:  # type: ignore[type-arg]
    """Сохраняет Redis-клиент в глобальном ресурсе.

    Args:
        client: Экземпляр Redis-клиента.
    """
    global _redis_client
    _redis_client = client


def get_redis_client() -> redis.Redis:  # type: ignore[type-arg]
    """Возвращает ранее инициализированный Redis-клиент.

    Returns:
        redis.Redis: Экземпляр Redis-клиента.

    Raises:
        RuntimeError: Если клиент ещё не был инициализирован.
    """
    if _redis_client is None:
        raise RuntimeError(
            "Redis-клиент ещё не инициализирован. "
            "Убедитесь, что lifecycle FastAPI уже запущен."
        )
    return _redis_client


def clear_redis_client() -> None:
    """Очищает ссылку на Redis-клиент (используется при shutdown)."""
    global _redis_client
    _redis_client = None

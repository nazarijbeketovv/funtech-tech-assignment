"""Интеграция с Redis (кеш)."""

from infra.cache.redis_client import RedisCacheClient

__all__ = ["RedisCacheClient"]

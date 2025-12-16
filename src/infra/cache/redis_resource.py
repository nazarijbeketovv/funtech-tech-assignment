from __future__ import annotations

import redis.asyncio as redis

_redis_client: redis.Redis | None = None  # type: ignore[type-arg]


def set_redis_client(client: redis.Redis) -> None:  # type: ignore[type-arg]
    global _redis_client
    _redis_client = client


def get_redis_client() -> redis.Redis:  # type: ignore[type-arg]
    if _redis_client is None:
        raise RuntimeError(
            "Redis client is not initialized yet. "
            "Make sure FastAPI lifespan has started."
        )
    return _redis_client


def clear_redis_client() -> None:
    global _redis_client
    _redis_client = None

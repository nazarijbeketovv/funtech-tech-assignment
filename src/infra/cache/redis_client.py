import logging
from dataclasses import dataclass

import redis.asyncio as redis

from application.interfaces.cache import CacheProtocol

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True, kw_only=True)
class RedisCacheClient(CacheProtocol):
    client: redis.Redis  # type: ignore[type-arg]
    ttl: int
    prefix: str = ""

    def _k(self, key: str) -> str:
        return f"{self.prefix}{key}"

    async def get(self, key: str) -> str | None:
        try:
            value = await self.client.get(self._k(key))
            return value
        except redis.RedisError as exc:
            logger.error(
                "Redis get failed",
                extra={"error": str(exc), "key": key, "full_key": self._k(key)},
            )
            return None

    async def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        try:
            await self.client.set(self._k(key), value, ex=ttl or self.ttl)
            return True
        except redis.RedisError as exc:
            logger.error(
                "Redis set failed",
                extra={"error": str(exc), "key": key, "full_key": self._k(key)},
            )
            return False

    async def delete(self, key: str) -> bool:
        try:
            await self.client.delete(self._k(key))
            return True
        except redis.RedisError as exc:
            logger.error(
                "Redis delete failed",
                extra={"error": str(exc), "key": key, "full_key": self._k(key)},
            )
            return False

    async def close(self) -> None:
        try:
            await self.client.close()
            await self.client.connection_pool.disconnect()
        except redis.RedisError:
            logger.warning("Failed to close redis client cleanly")

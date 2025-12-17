"""Реализация кеша на Redis."""

from dataclasses import dataclass

from loguru import logger
import redis.asyncio as redis

from application.interfaces.cache import CacheProtocol


@dataclass(slots=True, frozen=True, kw_only=True)
class RedisCacheClient(CacheProtocol):
    """Кеш-клиент на базе Redis.

    Attributes:
        client: Асинхронный Redis-клиент.
        ttl: TTL по умолчанию (секунды).
        prefix: Префикс для всех ключей.
    """

    client: redis.Redis  # type: ignore[type-arg]
    ttl: int
    prefix: str = ""

    def _k(self, key: str) -> str:
        """Формирует полный ключ с учётом префикса."""
        return f"{self.prefix}{key}"

    async def get(self, key: str) -> str | None:
        """Возвращает значение по ключу.

        Args:
            key: Ключ без префикса.

        Returns:
            str | None: Значение или `None` при отсутствии/ошибке Redis.
        """
        try:
            value = await self.client.get(self._k(key))
            return value
        except redis.RedisError as exc:
            logger.error(
                "Ошибка Redis при чтении",
                extra={"error": str(exc), "key": key, "full_key": self._k(key)},
            )
            return None

    async def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        """Сохраняет значение по ключу.

        Args:
            key: Ключ без префикса.
            value: Значение.
            ttl: TTL в секундах. Если `None`, используется `self.ttl`.

        Returns:
            bool: `True` при успехе, иначе `False`.
        """
        try:
            await self.client.set(self._k(key), value, ex=ttl or self.ttl)
            return True
        except redis.RedisError as exc:
            logger.error(
                "Ошибка Redis при записи",
                extra={"error": str(exc), "key": key, "full_key": self._k(key)},
            )
            return False

    async def delete(self, key: str) -> bool:
        """Удаляет значение по ключу.

        Args:
            key: Ключ без префикса.

        Returns:
            bool: `True` при успехе, иначе `False`.
        """
        try:
            await self.client.delete(self._k(key))
            return True
        except redis.RedisError as exc:
            logger.error(
                "Ошибка Redis при удалении",
                extra={"error": str(exc), "key": key, "full_key": self._k(key)},
            )
            return False

    async def close(self) -> None:
        """Закрывает соединение с Redis (best-effort)."""
        try:
            await self.client.close()
            await self.client.connection_pool.disconnect()
        except redis.RedisError:
            logger.warning("Не удалось корректно закрыть Redis-клиент")

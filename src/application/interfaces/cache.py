"""Контракт (Protocol) для кеша.

Интерфейс абстрагирует используемый кеш (например, Redis) от прикладных
сценариев.
"""

from typing import Protocol


class CacheProtocol(Protocol):
    """Протокол кеша, используемый use-case'ами."""

    async def get(self, key: str) -> str | None:
        """Получает значение по ключу.

        Args:
            key: Ключ в кеше.

        Returns:
            str | None: Значение, если ключ существует, иначе `None`.
        """
        ...

    async def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        """Сохраняет значение по ключу.

        Args:
            key: Ключ в кеше.
            value: Значение для сохранения.
            ttl: Время жизни в секундах. Если `None`, применяется дефолт клиента.

        Returns:
            bool: Признак успешного сохранения.
        """
        ...

    async def delete(self, key: str) -> bool:
        """Удаляет значение по ключу.

        Args:
            key: Ключ в кеше.

        Returns:
            bool: Признак того, что ключ был удалён.
        """
        ...

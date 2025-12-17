"""Контракты (Protocol) репозиториев.

Интерфейсы описывают операции доступа к данным, которые требуются прикладному
слою, не привязывая его к конкретной реализации (SQLAlchemy, внешние сервисы и
т.п.).
"""

from typing import Protocol
from uuid import UUID

from domain.entities.order import Order
from domain.entities.outbox_event import OutboxEvent
from domain.entities.user import User
from domain.value_objects.order_status import OrderStatus


class UserRepositoryProtocol(Protocol):
    """Протокол репозитория пользователей."""

    async def get_by_email(self, email: str) -> User | None:
        """Возвращает пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            User | None: Пользователь или `None`, если не найден.
        """
        ...

    async def get_by_id(self, user_id: int) -> User | None:
        """Возвращает пользователя по идентификатору.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            User | None: Пользователь или `None`, если не найден.
        """
        ...

    async def create(self, user: User) -> User:
        """Создаёт пользователя.

        Args:
            user: Доменная сущность пользователя.

        Returns:
            User: Созданная сущность (с заполненным `id` и `created_at`, если
            применимо).
        """
        ...


class OrderRepositoryProtocol(Protocol):
    """Протокол репозитория заказов."""

    async def create(self, order: Order) -> Order:
        """Создаёт заказ.

        Args:
            order: Доменная сущность заказа.

        Returns:
            Order: Созданная сущность.
        """
        ...

    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Возвращает заказ по идентификатору.

        Args:
            order_id: Идентификатор заказа.

        Returns:
            Order | None: Заказ или `None`, если не найден.
        """
        ...

    async def update_status(
        self, order_id: UUID, status: OrderStatus
    ) -> Order | None:
        """Обновляет статус заказа.

        Args:
            order_id: Идентификатор заказа.
            status: Новый статус.

        Returns:
            Order | None: Обновлённый заказ или `None`, если не найден.
        """
        ...

    async def list_by_user(self, user_id: int) -> list[Order]:
        """Возвращает список заказов пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            list[Order]: Заказы пользователя.
        """
        ...


class OutboxRepositoryProtocol(Protocol):
    """Протокол репозитория outbox-событий."""

    async def add(self, event: OutboxEvent) -> OutboxEvent:
        """Добавляет событие в outbox.

        Args:
            event: Доменная сущность события.

        Returns:
            OutboxEvent: Созданное событие.
        """
        ...

    async def list_pending(self, *, limit: int) -> list[OutboxEvent]:
        """Возвращает список необработанных событий.

        Args:
            limit: Максимальное количество возвращаемых событий.

        Returns:
            list[OutboxEvent]: Список событий.
        """
        ...

    async def mark_processed(self, event_id: UUID) -> None:
        """Помечает событие как обработанное.

        Args:
            event_id: Идентификатор события.
        """
        ...

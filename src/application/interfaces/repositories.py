from typing import Protocol
from uuid import UUID

from domain.entities.order import Order
from domain.entities.outbox_event import OutboxEvent
from domain.entities.user import User
from domain.value_objects.order_status import OrderStatus


class UserRepositoryProtocol(Protocol):
    async def get_by_email(self, email: str) -> User | None: ...

    async def get_by_id(self, user_id: int) -> User | None: ...

    async def create(self, user: User) -> User: ...


class OrderRepositoryProtocol(Protocol):
    async def create(self, order: Order) -> Order: ...

    async def get_by_id(self, order_id: UUID) -> Order | None: ...

    async def update_status(
        self, order_id: UUID, status: OrderStatus
    ) -> Order | None: ...

    async def list_by_user(self, user_id: int) -> list[Order]: ...


class OutboxRepositoryProtocol(Protocol):
    async def add(self, event: OutboxEvent) -> OutboxEvent: ...

    async def list_pending(self, *, limit: int) -> list[OutboxEvent]: ...

    async def mark_processed(self, event_id: UUID) -> None: ...

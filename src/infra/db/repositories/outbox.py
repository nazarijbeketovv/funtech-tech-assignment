"""Репозиторий outbox-событий на SQLAlchemy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.interfaces.repositories import OutboxRepositoryProtocol
from domain.entities.outbox_event import OutboxEvent
from infra.db.models import OutboxEventModel


@dataclass(slots=True, kw_only=True)
class OutboxRepositorySQLAlchemy(OutboxRepositoryProtocol):
    """SQLAlchemy-репозиторий outbox-событий."""

    session: AsyncSession

    async def add(self, event: OutboxEvent) -> OutboxEvent:
        """Добавляет событие в outbox.

        Args:
            event: Доменная сущность события.

        Returns:
            OutboxEvent: Созданное событие.
        """
        model = OutboxEventModel(
            id=event.id,
            event_type=event.event_type,
            payload=event.payload,
            created_at=event.created_at,
            processed_at=event.processed_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity_required(model)

    async def list_pending(self, *, limit: int) -> list[OutboxEvent]:
        """Возвращает список необработанных событий.

        Args:
            limit: Максимальное количество событий.

        Returns:
            list[OutboxEvent]: Список событий.
        """
        result = await self.session.execute(
            select(OutboxEventModel)
            .where(OutboxEventModel.processed_at.is_(None))
            .order_by(OutboxEventModel.created_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        models = result.scalars().all()
        return [self._to_entity_required(m) for m in models]

    async def mark_processed(self, event_id: UUID) -> None:
        """Помечает событие как обработанное.

        Args:
            event_id: Идентификатор события.
        """
        await self.session.execute(
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .values(processed_at=datetime.now(UTC))
        )

    def _to_entity_required(self, model: OutboxEventModel) -> OutboxEvent:
        """Преобразует ORM-модель outbox в доменную сущность."""
        return OutboxEvent(
            id=model.id,
            event_type=model.event_type,
            payload=model.payload,
            created_at=model.created_at,
            processed_at=model.processed_at,
        )

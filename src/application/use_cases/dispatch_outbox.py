"""Use-case отправки outbox-событий в брокер.

Сценарий выбирает необработанные события из БД и публикует их в брокер.
Используется для надёжной доставки сообщений при временных сбоях брокера.
"""

from __future__ import annotations

from dataclasses import dataclass

from application.interfaces.message_broker import MessageBrokerPublisherProtocol
from application.interfaces.uow import UnitOfWorkProtocol


@dataclass(slots=True, kw_only=True)
class DispatchOutboxUseCase:
    """Сценарий публикации pending-событий outbox."""

    uow: UnitOfWorkProtocol
    message_broker: MessageBrokerPublisherProtocol
    batch_size: int = 100

    async def __call__(self) -> int:
        """Публикует пачку outbox-событий и помечает их обработанными.

        Returns:
            int: Количество успешно обработанных событий.
        """
        async with self.uow:
            pending = await self.uow.outbox_repo.list_pending(
                limit=self.batch_size
            )
            processed = 0
            for event in pending:
                if event.event_type == "new_order":
                    await self.message_broker.publish_new_order(event.payload)
                    await self.uow.outbox_repo.mark_processed(event.id)
                    processed += 1
            await self.uow.commit()
            return processed

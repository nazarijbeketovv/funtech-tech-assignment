"""Доменная сущность outbox-события.

Outbox используется для надёжной доставки событий в брокер сообщений:
событие сначала сохраняется в БД в рамках транзакции, а затем отправляется
отдельным процессом/задачей с повторными попытками.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(slots=True, frozen=True, kw_only=True)
class OutboxEvent:
    """Событие в outbox-таблице.

    Attributes:
        event_type: Тип события (например, `new_order`).
        payload: Полезная нагрузка события (JSON-совместимый словарь).
        id: Идентификатор события (UUID).
        created_at: Время создания события (UTC).
        processed_at: Время обработки (UTC) или `None`, если не обработано.
    """

    event_type: str
    payload: dict[str, Any]
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    processed_at: datetime | None = None

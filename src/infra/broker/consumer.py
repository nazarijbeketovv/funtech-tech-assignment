"""Консьюмер событий `new_order` из RabbitMQ.

Реализован на FastStream. После получения события:
- выполняется простая дедупликация через Redis (ключ на сутки);
- событие передаётся в Celery-задачу `process_order_task`.
"""

import asyncio
import os
from typing import Any

import redis.asyncio as redis
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue
from pydantic import BaseModel, ValidationError
from uuid import UUID
from typing import Literal

from config.settings import settings
from infra.tasks.tasks import process_order_task

broker_url = os.getenv("BROKER_URL", "amqp://guest:guest@rabbitmq:5672/")
queue_name = os.getenv("BROKER_NEW_ORDER_QUEUE", "new_order")

broker = RabbitBroker(broker_url)
app = FastStream(broker)

_redis: redis.Redis | None = None  # type: ignore[type-arg]
_redis_lock = asyncio.Lock()


async def _get_redis() -> redis.Redis:  # type: ignore[type-arg]
    """Ленивая инициализация Redis-клиента для дедупликации.

    Returns:
        redis.Redis: Асинхронный Redis-клиент.
    """
    global _redis
    async with _redis_lock:
        if _redis is None:
            _redis = await redis.from_url(
                str(settings.redis_url),
                encoding="utf-8",
                decode_responses=True,
                health_check_interval=30,
            )
        return _redis


@app.on_shutdown
async def _shutdown() -> None:
    """Корректно закрывает Redis-клиент при остановке процесса."""
    global _redis
    if _redis is None:
        return
    try:
        await _redis.close()
        await _redis.connection_pool.disconnect()
    except Exception:
        # Очистка по принципу «по возможности».
        pass
    _redis = None


class NewOrderEvent(BaseModel):
    """Схема события `new_order`, ожидаемого из очереди."""

    event: Literal["new_order"]
    order_id: UUID
    user_id: int
    event_id: UUID | None = None


@broker.subscriber(RabbitQueue(queue_name, durable=True))
async def on_new_order(payload: dict[str, Any]) -> None:
    """Обрабатывает входящее событие `new_order`.

    Args:
        payload: Сырые данные события (обычно JSON из очереди).
    """
    try:
        event = NewOrderEvent.model_validate(payload)
    except ValidationError:
        return
    redis_client = await _get_redis()
    dedup_id = event.event_id or event.order_id
    dedup_key = f"order_service:new_order_event:{dedup_id}"
    is_first = await redis_client.set(dedup_key, "1", nx=True, ex=24 * 60 * 60)
    if not is_first:
        return
    process_order_task.delay(str(event.order_id))

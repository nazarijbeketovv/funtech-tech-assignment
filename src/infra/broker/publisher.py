from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any

import aio_pika

from application.interfaces.message_broker import (
    MessageBrokerPublisherProtocol,
)


@dataclass(slots=True, kw_only=True)
class RabbitPublisher(MessageBrokerPublisherProtocol):
    url: str
    queue_name: str
    retries: int = 3
    retry_backoff: float = 0.5

    _connection: aio_pika.RobustConnection | None = field(
        default=None, init=False, repr=False
    )
    _channel: aio_pika.RobustChannel | None = field(
        default=None, init=False, repr=False
    )
    _lock: asyncio.Lock = field(
        default_factory=asyncio.Lock, init=False, repr=False
    )

    async def publish_new_order(self, payload: dict[str, Any]) -> None:
        message_id: str | None = None
        raw_event_id = payload.get("event_id")
        if isinstance(raw_event_id, str) and raw_event_id:
            message_id = raw_event_id
        message = aio_pika.Message(
            body=json.dumps(payload).encode("utf-8"),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
            message_id=message_id,
        )

        last_exc: Exception | None = None
        attempts = max(1, int(self.retries))
        for attempt in range(1, attempts + 1):
            try:
                channel = await self._ensure_channel()
                await channel.default_exchange.publish(
                    message, routing_key=self.queue_name
                )
                return
            except Exception as exc:
                last_exc = exc
                await self._reset()
                if attempt >= attempts:
                    raise
                await asyncio.sleep(self.retry_backoff * (2 ** (attempt - 1)))

        if last_exc:
            raise last_exc

    async def close(self) -> None:
        await self._reset()

    async def _ensure_channel(self) -> aio_pika.RobustChannel:
        async with self._lock:
            if self._connection is None or self._connection.is_closed:
                self._connection = await aio_pika.connect_robust(self.url)
                self._channel = None
            if self._channel is None or self._channel.is_closed:
                self._channel = await self._connection.channel()
                await self._channel.declare_queue(self.queue_name, durable=True)
            return self._channel

    async def _reset(self) -> None:
        async with self._lock:
            if self._channel is not None:
                try:
                    await self._channel.close()
                except Exception:
                    pass
                self._channel = None
            if self._connection is not None:
                try:
                    await self._connection.close()
                except Exception:
                    pass
                self._connection = None

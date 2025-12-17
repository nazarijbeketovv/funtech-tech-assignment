"""Модуль middleware для трассировки запросов."""

import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from infra.logger.context import trace_id_var


class TraceIdMiddleware(BaseHTTPMiddleware):
    """Middleware для генерации и привязки trace_id к каждому входящему запросу.

    Attributes:
        app: ASGI приложение
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Обрабатывает входящий запрос, генерируя и привязывая trace_id.

        Args:
            request: Входящий HTTP запрос
            call_next: Функция для вызова следующего обработчика

        Returns:
            HTTP ответ
        """
        trace_id = uuid.uuid4().hex
        trace_id_var.set(trace_id)
        response = await call_next(request)
        return response

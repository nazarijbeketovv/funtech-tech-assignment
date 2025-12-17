"""Обработчики HTTP-запросов версии v1.

Модуль экспортирует роутеры для подключения в корневой `api_v1_router`.
"""

from api.v1.handlers.auth_controller import router as auth_router
from api.v1.handlers.orders_controller import (
    router as orders_router,
)

__all__ = ["auth_router", "orders_router"]

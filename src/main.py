"""Точка входа FastAPI-приложения.

Модуль собирает и конфигурирует приложение:
- инициализирует логирование;
- настраивает CORS;
- подключает контейнер зависимостей Dishka;
- регистрирует обработчики исключений;
- инициализирует Redis (кеш/лимитер) в lifespan.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import redis.asyncio as redis
import uvicorn
from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from loguru import logger

from api.error_handling import setup_exception_handlers
from api.v1 import api_v1_router
from config.ioc.di import get_providers
from config.settings import settings
from infra.cache.redis_resource import clear_redis_client, set_redis_client
from infra.logger.middleware import TraceIdMiddleware
from infra.logger.setup import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Жизненный цикл приложения (startup/shutdown).

    Инициализирует Redis-клиент, подключает его к лимитеру запросов и сохраняет
    ссылку на клиент в общем ресурсе кеша.

    Args:
        _: Экземпляр приложения FastAPI (не используется).

    Yields:
        None: Управление передаётся приложению на время работы.
    """
    logger.info("Запуск приложения...")
    redis_client: redis.Redis = await redis.from_url(  # type: ignore[type-arg]
        str(settings.redis_url),
        encoding="utf-8",
        decode_responses=True,
        health_check_interval=30,
    )
    set_redis_client(redis_client)
    await FastAPILimiter.init(redis_client)
    yield
    await FastAPILimiter.close()
    await redis_client.close()
    await redis_client.connection_pool.disconnect()
    clear_redis_client()
    logger.info("Остановка приложения...")


def create_app() -> FastAPI:
    """Создаёт и настраивает экземпляр FastAPI-приложения.

    Включает:
    - CORS middleware (параметры берутся из настроек);
    - контейнер зависимостей Dishka;
    - обработчики исключений;
    - роутер `v1` с глобальным rate limiting.

    Returns:
        FastAPI: Сконфигурированное приложение.
    """
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Сервис управления заказами",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(TraceIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.cors_origins,
        allow_credentials=settings.cors.cors_allow_credentials,
        allow_methods=settings.cors.cors_allow_methods,
        allow_headers=settings.cors.cors_allow_headers,
    )

    container: AsyncContainer = make_async_container(*get_providers())
    setup_dishka(container, app)

    setup_exception_handlers(app)
    app.include_router(
        api_v1_router,
        dependencies=[
            Depends(
                RateLimiter(times=settings.app.rate_limit_per_minute, seconds=60)
            )
        ],
    )

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

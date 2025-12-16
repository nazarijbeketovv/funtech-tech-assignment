from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
import redis.asyncio as redis
from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from config.ioc.di import get_providers
from config.logging import setup_logging
from api.error_handling import setup_exception_handlers
from api.v1 import api_v1_router
from config.settings import settings
from infra.cache.redis_resource import clear_redis_client, set_redis_client
import uvicorn

setup_logging(settings.log_level)
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting application...")
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
    logger.info("Shutting down application...")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Order management service",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

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

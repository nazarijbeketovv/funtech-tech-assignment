"""Фабрика асинхронных сессий SQLAlchemy."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(database_url: str, *, is_echo: bool = False) -> AsyncEngine:
    """Создаёт асинхронный движок SQLAlchemy.

    Args:
        database_url: DSN/URL подключения к БД.
        is_echo: Включить вывод SQL-запросов в лог.

    Returns:
        AsyncEngine: Асинхронный движок.
    """
    return create_async_engine(
        database_url,
        echo=is_echo,
        pool_pre_ping=True,
    )


def get_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Создаёт фабрику асинхронных сессий.

    Args:
        engine: Асинхронный движок.

    Returns:
        async_sessionmaker[AsyncSession]: Фабрика сессий.
    """
    return async_sessionmaker(engine, expire_on_commit=False)

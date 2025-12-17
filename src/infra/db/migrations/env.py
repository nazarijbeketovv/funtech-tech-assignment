"""Среда выполнения Alembic-миграций.

Этот файл используется Alembic при запуске команд `upgrade/downgrade/revision`.
Он настраивает `context` и подключение к БД (в online-режиме) для выполнения
миграций.

Примечания:
    - URL подключения берётся из конфигурации Alembic (`sqlalchemy.url`), которая,
      как правило, подхватывается из `alembic.ini` или переопределяется окружением
      (зависит от вашей настройки запуска миграций).
    - Модуль поддерживает два режима:
      - offline: генерация SQL без реального подключения;
      - online: подключение к БД и выполнение миграций.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from config.settings import settings
from infra.db.base import Base
from infra.db import models  # noqa: F401

config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", str(settings.database.database_url))


def run_migrations_offline() -> None:
    """Запускает миграции в offline-режиме (без подключения к БД).

    В offline-режиме Alembic формирует SQL-выражения, не открывая соединение.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Выполняет миграции в рамках переданного подключения.

    Args:
        connection: Подключение SQLAlchemy (sync), предоставляемое через
            `AsyncConnection.run_sync`.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Запускает миграции в online-режиме через асинхронный движок."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запускает online-миграции (обёртка над async-вариантом)."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

"""Сборка списка провайдеров Dishka для приложения."""

from dishka import Provider

from config.ioc.providers import (
    CacheProvider,
    MapperProvider,
    ProviderSet,
    RepositoryProvider,
    SettingsProvider,
    UnitOfWorkProvider,
    UseCaseProvider,
)


def get_providers() -> list[Provider]:
    """Возвращает список Dishka-провайдеров для контейнера.

    Returns:
        list[Provider]: Провайдеры, подключаемые в `main.py`.
    """
    return [
        SettingsProvider(),
        ProviderSet(),
        RepositoryProvider(),
        UnitOfWorkProvider(),
        CacheProvider(),
        MapperProvider(),
        UseCaseProvider(),
    ]

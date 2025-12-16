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
    return [
        SettingsProvider(),
        ProviderSet(),
        RepositoryProvider(),
        UnitOfWorkProvider(),
        CacheProvider(),
        MapperProvider(),
        UseCaseProvider(),
    ]

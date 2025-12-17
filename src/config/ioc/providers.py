"""Провайдеры зависимостей (Dependency Injection) для Dishka.

Модуль содержит набор классов-провайдеров, которые описывают, как создавать
и связывать зависимости приложения (настройки, сессии БД, репозитории, кеш,
публикатор событий и use-case'ы).
"""

from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.interfaces.repositories import (
    OrderRepositoryProtocol,
    OutboxRepositoryProtocol,
    UserRepositoryProtocol,
)
from application.interfaces.uow import UnitOfWorkProtocol
from application.services import PasswordHasher, TokenService
from application.use_cases import (
    CreateOrderUseCase,
    GetOrderUseCase,
    ListUserOrdersUseCase,
    LoginUserUseCase,
    RegisterUserUseCase,
    UpdateOrderStatusUseCase,
)
from config.base import Settings
from infra.broker import RabbitPublisher
from infra.cache import RedisCacheClient
from infra.cache.redis_resource import get_redis_client
from infra.db.repositories import (
    OrderRepositorySQLAlchemy,
    OutboxRepositorySQLAlchemy,
    UserRepositorySQLAlchemy,
)
from infra.db.session import create_engine, get_session_factory
from infra.db.uow import UnitOfWorkSQLAlchemy
from api.v1.mappers import OrderPresentationMapper


class SettingsProvider(Provider):
    """Провайдер настроек приложения."""

    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        """Возвращает экземпляр настроек приложения.

        Returns:
            Settings: Настройки приложения.
        """
        return Settings()


class ProviderSet(Provider):
    """Провайдер инфраструктурных зависимостей (БД/безопасность/брокер)."""

    @provide(scope=Scope.APP)
    async def get_session_factory(
        self, settings: Settings
    ) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
        """Создаёт фабрику асинхронных сессий SQLAlchemy.

        Живёт на уровне приложения и корректно освобождает engine при остановке.

        Args:
            settings: Настройки приложения.

        Yields:
            async_sessionmaker[AsyncSession]: Фабрика сессий.
        """
        engine = create_engine(settings.database_url, is_echo=settings.debug)
        factory = get_session_factory(engine)
        try:
            yield factory
        finally:
            await engine.dispose()

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[AsyncSession]:
        """Создаёт асинхронную сессию SQLAlchemy на запрос.

        Args:
            factory: Фабрика сессий.

        Yields:
            AsyncSession: Сессия SQLAlchemy.
        """
        async with factory() as session:
            yield session

    @provide(scope=Scope.APP)
    def get_password_hasher(self) -> PasswordHasher:
        """Создаёт сервис хеширования паролей."""
        return PasswordHasher()

    @provide(scope=Scope.APP)
    def get_token_service(self, settings: Settings) -> TokenService:
        """Создаёт сервис JWT-токенов.

        Args:
            settings: Настройки приложения.

        Returns:
            TokenService: Сервис токенов.
        """
        return TokenService(
            secret_key=settings.auth.jwt_secret_key,
            algorithm=settings.auth.jwt_algorithm,
            expires_delta=settings.auth.access_token_expire,
        )

    @provide(scope=Scope.APP)
    async def get_broker(
        self, settings: Settings
    ) -> AsyncIterator[RabbitPublisher]:
        """Создаёт publisher для брокера сообщений на уровне приложения.

        Args:
            settings: Настройки приложения.

        Yields:
            RabbitPublisher: Publisher для RabbitMQ.
        """
        publisher = RabbitPublisher(
            url=settings.broker.broker_url,
            queue_name=settings.broker.broker_new_order_queue,
            retries=settings.broker.publish_retries,
            retry_backoff=settings.broker.publish_retry_backoff,
        )
        try:
            yield publisher
        finally:
            await publisher.close()


class RepositoryProvider(Provider):
    """Провайдер репозиториев (реализации SQLAlchemy) на уровень запроса."""

    @provide(scope=Scope.REQUEST)
    def get_user_repository(
        self, session: AsyncSession
    ) -> UserRepositoryProtocol:
        """Создаёт репозиторий пользователей на запрос."""
        return UserRepositorySQLAlchemy(session=session)

    @provide(scope=Scope.REQUEST)
    def get_order_repository(
        self, session: AsyncSession
    ) -> OrderRepositoryProtocol:
        """Создаёт репозиторий заказов на запрос."""
        return OrderRepositorySQLAlchemy(session=session)

    @provide(scope=Scope.REQUEST)
    def get_outbox_repository(
        self, session: AsyncSession
    ) -> OutboxRepositoryProtocol:
        """Создаёт репозиторий outbox-событий на запрос."""
        return OutboxRepositorySQLAlchemy(session=session)


class UnitOfWorkProvider(Provider):
    """Провайдер Unit of Work на уровень запроса."""

    @provide(scope=Scope.REQUEST)
    def get_uow(
        self,
        session: AsyncSession,
        user_repo: UserRepositoryProtocol,
        order_repo: OrderRepositoryProtocol,
        outbox_repo: OutboxRepositoryProtocol,
    ) -> UnitOfWorkProtocol:
        """Создаёт Unit of Work на запрос.

        Args:
            session: SQLAlchemy-сессия.
            user_repo: Репозиторий пользователей.
            order_repo: Репозиторий заказов.
            outbox_repo: Репозиторий outbox.

        Returns:
            UnitOfWorkProtocol: Unit of Work.
        """
        return UnitOfWorkSQLAlchemy(
            session=session,
            user_repo=user_repo,
            order_repo=order_repo,
            outbox_repo=outbox_repo,
        )


class CacheProvider(Provider):
    """Провайдер кеша (Redis)."""

    @provide(scope=Scope.APP)
    def get_cache(
        self,
        settings: Settings,
    ) -> RedisCacheClient:
        """Создаёт кеш-клиент Redis.

        Args:
            settings: Настройки приложения.

        Returns:
            RedisCacheClient: Кеш-клиент Redis.
        """
        return RedisCacheClient(
            client=get_redis_client(),
            ttl=settings.redis.redis_cache_ttl,
            prefix=settings.redis.redis_cache_prefix,
        )


class MapperProvider(Provider):
    """Провайдер presentation-мапперов для API."""

    @provide(scope=Scope.REQUEST)
    def get_order_mapper(self) -> OrderPresentationMapper:
        """Создаёт маппер DTO → схема ответа для заказа."""
        return OrderPresentationMapper()


class UseCaseProvider(Provider):
    """Провайдер прикладных сценариев (use cases) на уровень запроса."""

    @provide(scope=Scope.REQUEST)
    def register_user_use_case(
        self, uow: UnitOfWorkProtocol, password_hasher: PasswordHasher
    ) -> RegisterUserUseCase:
        """Создаёт use-case регистрации пользователя."""
        return RegisterUserUseCase(uow=uow, password_hasher=password_hasher)

    @provide(scope=Scope.REQUEST)
    def login_user_use_case(
        self,
        users: UserRepositoryProtocol,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> LoginUserUseCase:
        """Создаёт use-case входа пользователя (выдачи токена)."""
        return LoginUserUseCase(
            users=users,
            password_hasher=password_hasher,
            token_service=token_service,
        )

    @provide(scope=Scope.REQUEST)
    def create_order_use_case(
        self,
        uow: UnitOfWorkProtocol,
        cache: RedisCacheClient,
        broker: RabbitPublisher,
        settings: Settings,
    ) -> CreateOrderUseCase:
        """Создаёт use-case создания заказа."""
        return CreateOrderUseCase(
            uow=uow,
            cache=cache,
            message_broker=broker,
            cache_ttl=settings.redis.redis_cache_ttl,
        )

    @provide(scope=Scope.REQUEST)
    def get_order_use_case(
        self, uow: UnitOfWorkProtocol, cache: RedisCacheClient, settings: Settings
    ) -> GetOrderUseCase:
        """Создаёт use-case получения заказа."""
        return GetOrderUseCase(
            uow=uow, cache=cache, cache_ttl=settings.redis.redis_cache_ttl
        )

    @provide(scope=Scope.REQUEST)
    def update_order_status_use_case(
        self, uow: UnitOfWorkProtocol, cache: RedisCacheClient, settings: Settings
    ) -> UpdateOrderStatusUseCase:
        """Создаёт use-case обновления статуса заказа."""
        return UpdateOrderStatusUseCase(
            uow=uow, cache=cache, cache_ttl=settings.redis.redis_cache_ttl
        )

    @provide(scope=Scope.REQUEST)
    def list_user_orders_use_case(
        self, uow: UnitOfWorkProtocol
    ) -> ListUserOrdersUseCase:
        """Создаёт use-case получения заказов пользователя."""
        return ListUserOrdersUseCase(uow=uow)

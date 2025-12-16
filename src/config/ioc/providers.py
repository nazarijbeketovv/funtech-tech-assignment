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
    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return Settings()


class ProviderSet(Provider):
    @provide(scope=Scope.APP)
    async def get_session_factory(
        self, settings: Settings
    ) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
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
        async with factory() as session:
            yield session

    @provide(scope=Scope.APP)
    def get_password_hasher(self) -> PasswordHasher:
        return PasswordHasher()

    @provide(scope=Scope.APP)
    def get_token_service(self, settings: Settings) -> TokenService:
        return TokenService(
            secret_key=settings.auth.jwt_secret_key,
            algorithm=settings.auth.jwt_algorithm,
            expires_delta=settings.auth.access_token_expire,
        )

    @provide(scope=Scope.APP)
    async def get_broker(
        self, settings: Settings
    ) -> AsyncIterator[RabbitPublisher]:
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
    @provide(scope=Scope.REQUEST)
    def get_user_repository(
        self, session: AsyncSession
    ) -> UserRepositoryProtocol:
        return UserRepositorySQLAlchemy(session=session)

    @provide(scope=Scope.REQUEST)
    def get_order_repository(
        self, session: AsyncSession
    ) -> OrderRepositoryProtocol:
        return OrderRepositorySQLAlchemy(session=session)

    @provide(scope=Scope.REQUEST)
    def get_outbox_repository(
        self, session: AsyncSession
    ) -> OutboxRepositoryProtocol:
        return OutboxRepositorySQLAlchemy(session=session)


class UnitOfWorkProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_uow(
        self,
        session: AsyncSession,
        user_repo: UserRepositoryProtocol,
        order_repo: OrderRepositoryProtocol,
        outbox_repo: OutboxRepositoryProtocol,
    ) -> UnitOfWorkProtocol:
        return UnitOfWorkSQLAlchemy(
            session=session,
            user_repo=user_repo,
            order_repo=order_repo,
            outbox_repo=outbox_repo,
        )


class CacheProvider(Provider):
    @provide(scope=Scope.APP)
    def get_cache(
        self,
        settings: Settings,
    ) -> RedisCacheClient:
        return RedisCacheClient(
            client=get_redis_client(),
            ttl=settings.redis.redis_cache_ttl,
            prefix=settings.redis.redis_cache_prefix,
        )


class MapperProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_order_mapper(self) -> OrderPresentationMapper:
        return OrderPresentationMapper()


class UseCaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def register_user_use_case(
        self, uow: UnitOfWorkProtocol, password_hasher: PasswordHasher
    ) -> RegisterUserUseCase:
        return RegisterUserUseCase(uow=uow, password_hasher=password_hasher)

    @provide(scope=Scope.REQUEST)
    def login_user_use_case(
        self,
        users: UserRepositoryProtocol,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> LoginUserUseCase:
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
        return GetOrderUseCase(
            uow=uow, cache=cache, cache_ttl=settings.redis.redis_cache_ttl
        )

    @provide(scope=Scope.REQUEST)
    def update_order_status_use_case(
        self, uow: UnitOfWorkProtocol, cache: RedisCacheClient, settings: Settings
    ) -> UpdateOrderStatusUseCase:
        return UpdateOrderStatusUseCase(
            uow=uow, cache=cache, cache_ttl=settings.redis.redis_cache_ttl
        )

    @provide(scope=Scope.REQUEST)
    def list_user_orders_use_case(
        self, uow: UnitOfWorkProtocol
    ) -> ListUserOrdersUseCase:
        return ListUserOrdersUseCase(uow=uow)

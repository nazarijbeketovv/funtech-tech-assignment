import asyncio
import time


from application.use_cases.dispatch_outbox import DispatchOutboxUseCase
from config.settings import settings
from infra.broker.publisher import RabbitPublisher
from infra.db.repositories import (
    OrderRepositorySQLAlchemy,
    OutboxRepositorySQLAlchemy,
    UserRepositorySQLAlchemy,
)
from infra.db.session import create_engine, get_session_factory
from infra.db.uow import UnitOfWorkSQLAlchemy
from infra.tasks.celery_app import celery_app


@celery_app.task(name="order_service.process_order_task")
def process_order_task(order_id: str) -> str:
    time.sleep(2)
    print(f"Order {order_id} processed")
    return order_id


@celery_app.task(name="order_service.dispatch_outbox_task")
def dispatch_outbox_task() -> int:
    async def _run() -> int:
        engine = create_engine(settings.database_url, is_echo=False)
        factory = get_session_factory(engine)
        publisher = RabbitPublisher(
            url=settings.broker.broker_url,
            queue_name=settings.broker.broker_new_order_queue,
            retries=settings.broker.publish_retries,
            retry_backoff=settings.broker.publish_retry_backoff,
        )
        try:
            async with factory() as session:
                session = session  # type: AsyncSession
                uow = UnitOfWorkSQLAlchemy(
                    session=session,
                    user_repo=UserRepositorySQLAlchemy(session=session),
                    order_repo=OrderRepositorySQLAlchemy(session=session),
                    outbox_repo=OutboxRepositorySQLAlchemy(session=session),
                )
                use_case = DispatchOutboxUseCase(
                    uow=uow, message_broker=publisher
                )
                return await use_case()
        finally:
            await publisher.close()
            await engine.dispose()

    return asyncio.run(_run())

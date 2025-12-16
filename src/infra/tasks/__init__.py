from infra.tasks.celery_app import celery_app
from infra.tasks.tasks import process_order_task

__all__ = ["celery_app", "process_order_task"]

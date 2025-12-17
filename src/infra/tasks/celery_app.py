"""Конфигурация Celery-приложения.

Используется для выполнения фоновых задач и периодического запуска
`dispatch_outbox_task` (Celery beat).
"""

import os

from celery import Celery

celery_app = Celery(
    "order_tasks",
    broker=os.getenv("CELERY_BROKER_URL", os.getenv("BROKER_URL", "")),
    backend=os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "")),
)

celery_app.conf.task_default_queue = "orders"
celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "dispatch-outbox-every-5s": {
        "task": "order_service.dispatch_outbox_task",
        "schedule": float(os.getenv("OUTBOX_DISPATCH_INTERVAL_SECONDS", "5")),
    }
}

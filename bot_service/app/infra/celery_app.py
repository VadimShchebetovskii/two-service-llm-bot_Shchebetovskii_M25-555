from celery import Celery
from app.core.config import settings


backend_url = settings.redis_url.replace("/0", "/1")

celery_app = Celery(
    "bot_service",
    broker=settings.rabbitmq_url,
    backend=backend_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
)


celery_app.autodiscover_tasks(["app.tasks"])
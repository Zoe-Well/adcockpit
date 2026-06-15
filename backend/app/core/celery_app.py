"""Celery app — async agent execution with Redis broker.

Fallback: synchronous execution if Redis unavailable (demo mode).
"""
import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

celery_app = Celery(
    "adcockpit",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_soft_time_limit=300,  # 5 min soft limit
    task_time_limit=600,       # 10 min hard limit
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["backend.app.tasks"], force=True)

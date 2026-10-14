"""Celery uygulaması. Uzun süren işler (tarama, PDF indirme/işaretleme, birleştirme) burada çalışır.

Başlatma (docker-compose 'worker' servisi bunu otomatik yapar):
    celery -A app.worker worker --loglevel=info
"""
from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery("tesvik", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_track_started=True,
    result_expires=60 * 60 * 24,
    timezone="Europe/Istanbul",
)
celery_app.autodiscover_tasks(["app.pipeline"], related_name="tasks")

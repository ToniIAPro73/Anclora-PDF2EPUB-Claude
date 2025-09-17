"""Centralized Celery application factory for the Anclora backend."""
import os
import threading
from typing import Dict, Optional

from celery import Celery
from kombu import Queue

from .config import ConfigManager
from . import create_app

try:  # Optional typing without importing Flask at runtime
    from flask import Flask
except ImportError:  # pragma: no cover - typing only
    Flask = object  # type: ignore

_app_lock = threading.Lock()
_flask_app: Optional["Flask"] = None
_celery_app: Optional[Celery] = None


def _str_to_bool(value: Optional[str], default: bool = False) -> bool:
    """Convert string environment values to boolean."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _build_queues(default_queue: str) -> Dict[str, Queue]:
    """Create celery queues from environment configuration."""
    queues = {default_queue: Queue(default_queue)}
    additional = os.getenv("CELERY_ADDITIONAL_QUEUES", "")
    for raw_name in additional.split(","):
        name = raw_name.strip()
        if name and name not in queues:
            queues[name] = Queue(name)
    return queues


def get_flask_app() -> "Flask":
    """Return a singleton Flask app instance for Celery workers."""
    global _flask_app
    if _flask_app is None:
        with _app_lock:
            if _flask_app is None:
                ConfigManager.initialize(strict_mode=False)
                _flask_app = create_app()
    return _flask_app  # type: ignore[return-value]


def get_celery_app() -> Celery:
    """Return a configured Celery instance."""
    global _celery_app
    if _celery_app is not None:
        return _celery_app

    with _app_lock:
        if _celery_app is None:
            ConfigManager.initialize(strict_mode=False)

            broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
            result_backend = os.getenv("CELERY_RESULT_BACKEND", broker_url)
            default_queue = os.getenv("CELERY_DEFAULT_QUEUE", "conversions")

            celery = Celery("anclora")
            celery.conf.update(
                broker_url=broker_url,
                result_backend=result_backend,
                task_default_queue=default_queue,
                task_acks_late=_str_to_bool(os.getenv("CELERY_TASK_ACKS_LATE"), True),
                task_track_started=True,
                worker_prefetch_multiplier=int(os.getenv("CELERY_PREFETCH_MULTIPLIER", "1")),
                task_time_limit=int(os.getenv("CELERY_TASK_TIME_LIMIT", "900")),
                task_soft_time_limit=int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", "600")),
                task_default_retry_delay=int(os.getenv("CELERY_TASK_RETRY_DELAY", "30")),
                broker_connection_retry_on_startup=True,
                result_expires=int(os.getenv("CELERY_RESULT_EXPIRES", "3600")),
            )

            rate_limit = os.getenv("CELERY_TASK_RATE_LIMIT")
            if rate_limit:
                celery.conf.task_default_rate_limit = rate_limit

            visibility_timeout = os.getenv("CELERY_VISIBILITY_TIMEOUT")
            if visibility_timeout:
                celery.conf.broker_transport_options = {
                    "visibility_timeout": int(visibility_timeout)
                }

            queues = _build_queues(default_queue)
            celery.conf.task_queues = list(queues.values())

            routes_env = os.getenv("CELERY_TASK_ROUTES")
            if routes_env:
                # Expected format: task_name=queue,other_task=queue2
                routes: Dict[str, Dict[str, str]] = {}
                for chunk in routes_env.split(","):
                    if "=" in chunk:
                        task_name, queue_name = [part.strip() for part in chunk.split("=", 1)]
                        if task_name and queue_name:
                            routes[task_name] = {"queue": queue_name}
                if routes:
                    celery.conf.task_routes = routes

            celery.autodiscover_tasks(["backend.app"])

            _celery_app = celery

    return _celery_app


# Eagerly expose Celery instance for backwards compatibility with `celery -A app.tasks`
celery_app = get_celery_app()

# Expose Flask app singleton for easy imports
flask_app = get_flask_app()

import os
import time
import logging
import json
from celery import Celery
from celery.signals import task_prerun, task_postrun
from prometheus_client import Counter, Histogram, start_http_server

from app.converter import EnhancedPDFToEPUBConverter
from .models import Conversion
from . import db


celery_app = Celery(
    "tasks",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)


class JsonFormatter(logging.Formatter):
    """Simple JSON formatter for Celery logs."""

    def format(self, record):  # type: ignore[override]
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
        }
        for key in ["task_name", "task_id", "status", "duration"]:
            if hasattr(record, key):
                log_record[key] = getattr(record, key)
        return json.dumps(log_record)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
root = logging.getLogger()
root.handlers = [handler]
root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

TASK_COUNT = Counter(
    "celery_tasks_total", "Total Celery tasks", ["name", "status"]
)
TASK_LATENCY = Histogram(
    "celery_task_duration_seconds", "Celery task duration", ["name"]
)

if os.environ.get("WORKER_METRICS_PORT"):
    start_http_server(int(os.environ["WORKER_METRICS_PORT"]))

converter = EnhancedPDFToEPUBConverter()


@task_prerun.connect
def _task_prerun(sender=None, task_id=None, **kwargs):  # pragma: no cover
    sender.__start_time = time.time()
    logger.info("task start", extra={"task_name": sender.name, "task_id": task_id})


@task_postrun.connect
def _task_postrun(sender=None, task_id=None, state=None, **kwargs):  # pragma: no cover
    duration = time.time() - getattr(sender, "__start_time", time.time())
    TASK_COUNT.labels(sender.name, state).inc()
    TASK_LATENCY.labels(sender.name).observe(duration)
    logger.info(
        "task end",
        extra={
            "task_name": sender.name,
            "task_id": task_id,
            "status": state,
            "duration": duration,
        },
    )


@celery_app.task(name="convert_pdf_to_epub")
def convert_pdf_to_epub(task_id, input_path, output_path=None):
    """Convert a PDF file to EPUB capturing metrics and updating history."""
    start_time = time.time()
    try:
        result = converter.convert(input_path, output_path)
        duration = time.time() - start_time
        metrics = {
            "duration": duration,
            "quality_metrics": result.get("quality_metrics"),
            "engine_used": result.get("engine_used"),
            "analysis": result.get("analysis"),
            "pipeline_used": result.get("pipeline_used"),
            "pipeline_metrics": result.get("pipeline_metrics"),
        }
        from . import create_app
        app = create_app()
        with app.app_context():
            conv = Conversion.query.filter_by(task_id=task_id).first()
            if conv:
                conv.status = "SUCCESS"
                conv.output_path = result.get("output_path")
                conv.metrics = metrics
                db.session.commit()
        return {
            "task_id": task_id,
            "success": result.get("success", False),
            "output_path": result.get("output_path"),
            "message": result.get("message"),
            "quality_metrics": result.get("quality_metrics"),
            "engine_used": result.get("engine_used"),
            "analysis": result.get("analysis"),
            "pipeline_used": result.get("pipeline_used"),
            "pipeline_metrics": result.get("pipeline_metrics"),
            "duration": duration,
        }
    except Exception as exc:
        duration = time.time() - start_time
        logger.exception("Error converting PDF to EPUB", extra={"task_id": task_id})
        metrics = {
            "duration": duration,
            "error": str(exc),
        }
        from . import create_app
        app = create_app()
        with app.app_context():
            conv = Conversion.query.filter_by(task_id=task_id).first()
            if conv:
                conv.status = "FAILURE"
                conv.output_path = None
                conv.metrics = metrics
                db.session.commit()
        return {
            "task_id": task_id,
            "success": False,
            "output_path": None,
            "message": str(exc),
            "duration": duration,
        }


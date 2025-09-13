import os
import time
import logging
from celery import Celery

from app.converter import EnhancedPDFToEPUBConverter
from .models import init_db, update_conversion

celery_app = Celery(
    'tasks',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

converter = EnhancedPDFToEPUBConverter()
init_db()


@celery_app.task(name='convert_pdf_to_epub')
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
        }
        update_conversion(task_id, "SUCCESS", result.get("output_path"), metrics)
        return {
            "task_id": task_id,
            "success": result.get("success", False),
            "output_path": result.get("output_path"),
            "message": result.get("message"),
            "quality_metrics": result.get("quality_metrics"),
            "engine_used": result.get("engine_used"),
            "analysis": result.get("analysis"),
            "duration": duration,
        }
    except Exception as exc:
        duration = time.time() - start_time
        logging.exception("Error converting PDF to EPUB")
        metrics = {
            "duration": duration,
            "error": str(exc),
        }
        update_conversion(task_id, "FAILURE", None, metrics)
        return {
            "task_id": task_id,
            "success": False,
            "output_path": None,
            "message": str(exc),
            "duration": duration,
        }


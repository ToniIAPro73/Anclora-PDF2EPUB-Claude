import os
import time
import logging
from pathlib import Path
from celery import Celery
from dotenv import load_dotenv

# Load environment variables from .env located at repository root
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / '.env')

# Build Redis URL from environment variables
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = os.environ.get('REDIS_PORT', '6379')
redis_password = os.environ.get('REDIS_PASSWORD', '')
redis_auth = f":{redis_password}@" if redis_password else ""
redis_url = f"redis://{redis_auth}{redis_host}:{redis_port}/0"

broker_url = os.environ.get('CELERY_BROKER_URL', redis_url)
backend_url = os.environ.get('CELERY_RESULT_BACKEND', redis_url)

celery_app = Celery('tasks', broker=broker_url, backend=backend_url)

from app.converter import EnhancedPDFToEPUBConverter
converter = EnhancedPDFToEPUBConverter()

@celery_app.task(name='convert_pdf_to_epub')
def convert_pdf_to_epub(task_id, input_path, output_path=None):
    """Convert a PDF file to EPUB capturing metrics and errors."""
    start_time = time.time()
    try:
        result = converter.convert(input_path, output_path)
        duration = time.time() - start_time
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
        return {
            "task_id": task_id,
            "success": False,
            "output_path": None,
            "message": str(exc),
            "duration": duration,
        }

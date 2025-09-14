import os
import time
import logging
import json
from celery import Celery
from celery.signals import task_prerun, task_postrun
from prometheus_client import Counter, Histogram, start_http_server

from app.converter import EnhancedPDFToEPUBConverter, ConversionEngine
from .supabase_client import update_conversion_status, get_conversion_by_task_id


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

# Metrics for individual pipeline steps
PIPELINE_STEP_COUNT = Counter(
    "pipeline_steps_total", "Total pipeline steps executed", ["task", "step", "status"]
)
PIPELINE_STEP_LATENCY = Histogram(
    "pipeline_step_duration_seconds", "Pipeline step duration in seconds", ["task", "step"]
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


@celery_app.task(bind=True, name="convert_pdf_to_epub")

def convert_pdf_to_epub(self, task_id, input_path, output_path=None, pipeline=None):
    """Convert a PDF to EPUB executing each step in the provided pipeline.

    Args:
        task_id: Identifier used to track conversion in the database.
        input_path: Path to the source PDF file.
        output_path: Optional path for the generated EPUB.
        pipeline: List of step names to execute sequentially. Supported steps:
            ``analysis`` and ``conversion``.
    """

    start_time = time.time()
    pipeline = pipeline or ["conversion"]
    total_steps = len(pipeline)
    pipeline_metrics = []

    from . import create_app
    app = create_app()

    if not getattr(self.request, "id", None):
        self.request.id = task_id

    logger.info(
        "pipeline start",
        extra={"task_id": task_id, "task_name": "convert_pdf_to_epub", "pipeline": pipeline},
    )
    def _update(state, meta):
        try:
            self.update_state(state=state, meta=meta)
        except Exception:
            pass

    context = {}
    for i, step in enumerate(pipeline):
        progress = int((i / total_steps) * 100)
        _update("PROGRESS", {"progress": progress, "message": f"Iniciando {step}"})
        step_start = time.time()
        step_status = "SUCCESS"
        try:
            logger.info(
                "step start",
                extra={"task_id": task_id, "task_name": "convert_pdf_to_epub", "step": step},
            )
            if step == "analysis":
                analysis = converter.analyzer.analyze_pdf(input_path)
                context["analysis"] = {
                    "page_count": analysis.page_count,
                    "file_size": analysis.file_size,
                    "content_type": analysis.content_type.value,
                    "complexity_score": analysis.complexity_score,
                    "issues": analysis.issues,
                    "language": analysis.language,
                }
            elif step in {"conversion", "convert"}:
                result = converter.convert(input_path, output_path)
                context["conversion"] = result
                output_path = result.get("output_path")
                if not result.get("success", False):
                    step_status = "FAILURE"
            else:
                raise ValueError(f"Unknown pipeline step: {step}")
        except Exception as exc:  # pragma: no cover - unexpected failures
            step_status = "FAILURE"
            context[step] = {"error": str(exc)}
            logger.exception(
                "step error",
                extra={
                    "task_id": task_id,
                    "task_name": "convert_pdf_to_epub",
                    "step": step,
                },
            )

        step_duration = time.time() - step_start
        pipeline_metrics.append(
            {"step": step, "status": step_status, "duration": step_duration}
        )
        PIPELINE_STEP_COUNT.labels("convert_pdf_to_epub", step, step_status).inc()
        PIPELINE_STEP_LATENCY.labels("convert_pdf_to_epub", step).observe(step_duration)
        logger.info(
            "step end",
            extra={
                "task_id": task_id,
                "task_name": "convert_pdf_to_epub",
                "step": step,
                "status": step_status,
                "duration": step_duration,
            },
        )

        # Update conversion status in Supabase
        conv = get_conversion_by_task_id(task_id)
        if conv:
            metrics = conv.get('metrics') or {}
            metrics.setdefault("pipeline", []).append(
                {"step": step, "status": step_status, "duration": step_duration}
            )

            update_data = {"metrics": metrics}

            if step in {"conversion", "convert"} and step_status == "SUCCESS":
                update_data["output_path"] = output_path

            if step_status == "FAILURE":
                update_data["status"] = "FAILED"
                update_data["output_path"] = None
                metrics["error"] = context.get(step, {}).get("error")
                update_data["metrics"] = metrics
            else:
                update_data["status"] = "PROCESSING"

            update_conversion_status(task_id, update_data["status"], **{k: v for k, v in update_data.items() if k != "status"})
        if step_status == "FAILURE":
            error_msg = context.get(step, {}).get("error", "Unknown error")
            total_duration = time.time() - start_time
            _update("FAILURE", {"progress": progress, "message": error_msg})
            context["conversion"] = {
                "success": False,
                "message": error_msg,
                "output_path": None,
            }
            break
        progress = int(((i + 1) / total_steps) * 100)
        _update("PROGRESS", {"progress": progress, "message": f"Completado {step}"})

    total_duration = time.time() - start_time
    final_result = context.get("conversion", {})
    _update("PROGRESS", {"progress": 100, "message": "Proceso completado"})

    # Update final conversion status in Supabase
    conv = get_conversion_by_task_id(task_id)
    if conv:
        final_status = "COMPLETED" if conv.get("status") != "FAILED" else "FAILED"
        metrics = conv.get('metrics') or {}
        metrics["duration"] = total_duration

        if final_result.get("engine_used"):
            metrics["engine_used"] = final_result.get("engine_used")
        if final_result.get("quality_metrics"):
            metrics["quality_metrics"] = final_result.get("quality_metrics")

        update_data = {"metrics": metrics}

        # Generate thumbnail for the source PDF
        try:
            from pdf2image import convert_from_path  # type: ignore

            with app.app_context():
                thumb_dir = app.config.get("THUMBNAIL_FOLDER", "thumbnails")
                os.makedirs(thumb_dir, exist_ok=True)
                thumb_filename = f"{task_id}.png"
                thumb_path = os.path.join(thumb_dir, thumb_filename)
                images = convert_from_path(input_path, first_page=1, last_page=1)
                if images:
                    images[0].save(thumb_path, "PNG")
                    update_data["thumbnail_path"] = thumb_filename
        except Exception:  # pragma: no cover - optional thumbnail generation
            logger.exception("thumbnail generation failed", extra={"task_id": task_id})

        update_conversion_status(task_id, final_status, **update_data)

    return {
        "task_id": task_id,
        "success": final_result.get("success", True),
        "output_path": final_result.get("output_path"),
        "message": final_result.get("message"),
        "quality_metrics": final_result.get("quality_metrics"),
        "engine_used": final_result.get("engine_used"),
        "analysis": final_result.get("analysis") or context.get("analysis"),
        "duration": total_duration,
        "pipeline": pipeline_metrics,
    }


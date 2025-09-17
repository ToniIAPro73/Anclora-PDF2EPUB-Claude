from flask import Flask, Response, request, jsonify
from . import config  # Import config to load environment variables
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import os
import time
import logging
import json
from flask_cors import CORS  # Importamos CORS
# from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

limiter = Limiter(key_func=get_remote_address)

class JsonFormatter(logging.Formatter):
    """Simple JSON formatter for structured logs."""
    def format(self, record):  # type: ignore[override]
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
        }
        for key in ["method", "path", "status", "duration", "task_id", "task_name"]:
            if hasattr(record, key):
                log_record[key] = getattr(record, key)
        return json.dumps(log_record)


# REQUEST_COUNT = Counter(
#     "http_requests_total", "Total HTTP requests", ["method", "endpoint", "http_status"]
# )
# REQUEST_LATENCY = Histogram(
#     "http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"]
# )

def create_app():
    app = Flask(__name__)
    
    # Habilitamos CORS para todas las rutas
    # Configuración específica para desarrollo - permite localhost en diferentes puertos
    allowed_origins = [
        "http://localhost:5178",  # Frontend dev server
        "http://127.0.0.1:5178",  # Alternative localhost
        "http://localhost:3000",  # Alternative frontend port
        "http://127.0.0.1:3000"   # Alternative localhost
    ]
    CORS(app,
         resources={r"/*": {"origins": allowed_origins}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.DEBUG)  # Changed to DEBUG for more verbose logging
    app.logger = logging.getLogger(__name__)
    app.logger.setLevel(logging.DEBUG)

    # Configuración desde variables de entorno
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', 'uploads'),
        RESULTS_FOLDER=os.environ.get('RESULTS_FOLDER', 'results'),
        THUMBNAIL_FOLDER=os.environ.get('THUMBNAIL_FOLDER', 'thumbnails'),
        CONVERSION_TIMEOUT=int(os.environ.get('CONVERSION_TIMEOUT', 300)),
        RATE_LIMIT=os.environ.get('RATE_LIMIT', '5 per minute'),
        JWT_SECRET=os.environ.get('JWT_SECRET', 'dev'),
        JWT_EXPIRATION=int(os.environ.get('JWT_EXPIRATION', 3600)),
        CELERY_DEFAULT_QUEUE=os.environ.get('CELERY_DEFAULT_QUEUE', 'conversions'),
        CELERY_CONVERSION_QUEUE=os.environ.get('CELERY_CONVERSION_QUEUE', os.environ.get('CELERY_DEFAULT_QUEUE', 'conversions')),
        CELERY_TASK_EXPIRES=int(os.environ.get('CELERY_TASK_EXPIRES', 3600)),
    )

    limiter.init_app(app)

    # Asegurarse de que existan los directorios
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["RESULTS_FOLDER"], exist_ok=True)
    os.makedirs(app.config["THUMBNAIL_FOLDER"], exist_ok=True)

    @app.before_request
    def start_timer():  # pragma: no cover - simple middleware
        request.start_time = time.time()

    @app.after_request
    def log_request(response):  # pragma: no cover - simple middleware
        latency = time.time() - getattr(request, "start_time", time.time())
        # REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
        # REQUEST_LATENCY.labels(request.method, request.path).observe(latency)
        app.logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration": latency,
            },
        )
        return response

    # @app.route("/metrics")
    # def metrics():
    #     return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    # Registrar rutas
    # from . import routes  # Temporary disabled due to circular import
    from . import test_routes
    from . import credits_routes  # Sistema de créditos
    from . import simple_routes  # Temporary enabled for basic functionality

    # app.register_blueprint(routes.bp)  # Temporarily disabled
    app.register_blueprint(test_routes.test_bp)
    app.register_blueprint(credits_routes.bp)  # Rutas de créditos
    app.register_blueprint(simple_routes.bp)  # Simple routes for basic functionality
    # app.register_blueprint(simple_routes.bp)  # Disabled for now

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "error": "ratelimit exceeded",
            "message": str(e.description),
        }), 429

    return app

from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
import time
import logging
import json
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from .models import init_db

db = SQLAlchemy()
migrate = Migrate()


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


REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"]
)

def create_app():
    app = Flask(__name__)

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
    app.logger = logging.getLogger(__name__)

    # Configuración desde variables de entorno
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', 'uploads'),
        RESULTS_FOLDER=os.environ.get('RESULTS_FOLDER', 'results'),
        CONVERSION_TIMEOUT=int(os.environ.get('CONVERSION_TIMEOUT', 300)),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)
    migrate.init_app(app, db)
    
    # Asegurarse de que existan los directorios
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["RESULTS_FOLDER"], exist_ok=True)

    @app.before_request
    def start_timer():  # pragma: no cover - simple middleware
        request.start_time = time.time()

    @app.after_request
    def log_request(response):  # pragma: no cover - simple middleware
        latency = time.time() - getattr(request, "start_time", time.time())
        REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
        REQUEST_LATENCY.labels(request.method, request.path).observe(latency)
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

    @app.route("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    # Inicializar base de datos y registrar rutas
    init_db()
    from . import routes

    app.register_blueprint(routes.bp)

    return app


class Conversion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    metrics = db.Column(db.JSON)

# Para ejecución directa
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('FLASK_RUN_PORT', 5175))
    app.run(host='0.0.0.0', port=port)

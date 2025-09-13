from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from .models import init_db
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
limit_value = lambda: os.environ.get('RATE_LIMIT', '5 per minute')
limiter = Limiter(get_remote_address, default_limits=[limit_value])
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Configuración desde variables de entorno
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', 'uploads'),
        RESULTS_FOLDER=os.environ.get('RESULTS_FOLDER', 'results'),
        CONVERSION_TIMEOUT=int(os.environ.get('CONVERSION_TIMEOUT', 300)),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        RATE_LIMIT=os.environ.get('RATE_LIMIT', '5 per minute'),
    )

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    
    # Asegurarse de que existan los directorios
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    
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

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from .models import init_db

db = SQLAlchemy()
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
        JWT_SECRET=os.environ.get('JWT_SECRET', 'dev'),
        JWT_EXPIRATION=int(os.environ.get('JWT_EXPIRATION', 3600)),
    )

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()
    
    # Asegurarse de que existan los directorios
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    
    # Inicializar base de datos y registrar rutas
    init_db()
    from . import routes
    from .auth import auth_bp
    app.register_blueprint(routes.bp)
    app.register_blueprint(auth_bp)

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

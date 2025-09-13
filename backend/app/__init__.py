from flask import Flask
import os
from .models import init_db

def create_app():
    app = Flask(__name__)
    
    # Configuración desde variables de entorno
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', 'uploads'),
        RESULTS_FOLDER=os.environ.get('RESULTS_FOLDER', 'results'),
        CONVERSION_TIMEOUT=int(os.environ.get('CONVERSION_TIMEOUT', 300)),
    )
    
    # Asegurarse de que existan los directorios
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    
    # Inicializar base de datos y registrar rutas
    init_db()
    from . import routes
    app.register_blueprint(routes.bp)

    return app

# Para ejecución directa
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('FLASK_RUN_PORT', 5175))
    app.run(host='0.0.0.0', port=port)
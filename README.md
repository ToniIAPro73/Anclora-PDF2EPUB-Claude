Anclora PDF2EPUB
Sistema de conversión inteligente de documentos PDF a formato EPUB3, diseñado para abordar los problemas más comunes en este tipo de conversiones.
Mostrar imagen
Características Principales

🔍 Análisis automático con IA: Detecta problemas y selecciona el motor óptimo
🚀 Múltiples motores especializados: Adaptación según el tipo de contenido
📊 Transparencia total: Logs detallados y métricas en tiempo real
⚡ Arquitectura Cloud-Ready: Escalable para millones de conversiones
🌗 Tema Claro/Oscuro: Soporte completo para ambos modos
🔄 OCR integrado: Procesamiento de documentos escaneados
📝 Manejo de fórmulas matemáticas: Preservación de ecuaciones en formato MathML
🖼️ Optimización inteligente de imágenes: Preservación de calidad y posicionamiento

Arquitectura del Sistema
┌─────────────────────────────────────────────────────────┐
│ ANCLORA PDF2EPUB                                        │
├─────────────────────────────────────────────────────────┤
│ Frontend: React + TypeScript + Tailwind CSS             │
├─────────────────────────────────────────────────────────┤
│ API Gateway: Flask + Authentication + Rate Limiting     │
├─────────────────────────────────────────────────────────┤
│ Message Queue: Redis + Celery (Async Processing)        │
├─────────────────────────────────────────────────────────┤
│ Conversion Engine: Multi-Format Intelligent Processor   │
│ ├── Basic Conversions (PyMuPDF + EbookLib)             │
│ ├── Advanced Formats (OCR + specialized libraries)      │
│ ├── AI Enhancement (Analysis + quality optimization)    │
│ └── Monitoring (Logs + custom metrics)                  │
├─────────────────────────────────────────────────────────┤
│ Data Layer: File Storage + Metadata + Logs              │
├─────────────────────────────────────────────────────────┤
│ Infrastructure: Docker + Nginx + Health Checks          │
└─────────────────────────────────────────────────────────┘
Requisitos Previos

Docker y Docker Compose
Node.js 16+ (solo para desarrollo local)
Python 3.9+ (solo para desarrollo local)

Inicio Rápido

Clonar el repositorio:

bashgit clone https://github.com/tu-usuario/anclora-pdf2epub.git
cd anclora-pdf2epub

Configurar el archivo .env en la raíz del proyecto:

env# Configuración de puertos
FRONTEND_PORT=3003
BACKEND_PORT=5175
NGINX_PORT=80

# Configuración de Redis
REDIS_PORT=6379
REDIS_PASSWORD=anclora_redis_password

# Configuración de la aplicación
FLASK_ENV=development
FLASK_APP=app
SECRET_KEY=anclora_dev_secret_key

# Configuración de almacenamiento
UPLOAD_FOLDER=uploads
RESULTS_FOLDER=results

# Configuración de recursos
MAX_WORKERS=4
CONVERSION_TIMEOUT=300

Iniciar con Docker Compose:

bashdocker-compose up -d

Acceder a la aplicación:

http://localhost           # A través de Nginx
http://localhost:3003      # Frontend directo
http://localhost:5175/api  # Backend API directo
Desarrollo Local
Frontend
bashcd frontend
npm install
npm start
El servidor de desarrollo iniciará en http://localhost:3003
Backend
bashcd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run --port=5175
La API estará disponible en http://localhost:5175
Pruebas
bashpytest
Estructura del Proyecto
anclora-pdf2epub/
├── frontend/                 # Aplicación React + TypeScript
│   ├── public/               # Archivos estáticos
│   │   └── images/           # Imágenes y assets
│   ├── src/                  # Código fuente
│   │   ├── components/       # Componentes React
│   │   ├── hooks/            # Custom React hooks
│   │   ├── utils/            # Utilidades
│   │   ├── styles/           # CSS/Tailwind
│   │   ├── App.tsx           # Componente principal
│   │   └── index.tsx         # Punto de entrada
│   ├── package.json          # Dependencias npm
│   ├── tsconfig.json         # Configuración TypeScript
│   └── vite.config.js        # Configuración Vite
│
├── backend/                  # API Flask + Celery
│   ├── app/                  # Aplicación Flask
│   │   ├── __init__.py       # Factory app
│   │   ├── routes.py         # Endpoints API
│   │   ├── tasks.py          # Tareas Celery
│   │   ├── converter.py      # Motor conversión
│   │   └── models/           # Modelos de datos
│   ├── tests/                # Tests unitarios/integración
│   └── requirements.txt      # Dependencias Python
│
├── docker/                   # Configuración Docker
│   ├── nginx/                # Configuración Nginx
│   │   └── nginx.conf        # Proxy reverso
│   ├── Dockerfile.frontend   # Imagen Docker frontend
│   └── Dockerfile.backend    # Imagen Docker backend
│
├── .env                      # Variables de entorno
├── docker-compose.yml        # Orquestación servicios
└── README.md                 # Documentación
Uso del Sistema
1. Subir un PDF

Arrastra y suelta un archivo PDF en la zona de carga o haz clic para seleccionarlo
Se realizará un análisis automático del documento para detectar su complejidad y recomendaciones

2. Iniciar Conversión

Una vez subido el archivo, presiona el botón "Iniciar Conversión"
El sistema seleccionará automáticamente el motor de conversión óptimo según la complejidad detectada
Puedes ver el progreso en tiempo real con detalles de cada etapa

3. Descargar el EPUB

Al completar la conversión, se mostrarán métricas de calidad
El botón "Descargar EPUB" te permitirá guardar el archivo convertido
También puedes ver una vista previa del resultado antes de descargar

Motores de Conversión
El sistema utiliza tres motores especializados:

Motor Rápido (Rapid)

Para documentos simples basados principalmente en texto
Tiempo típico: 3-5 segundos
Mejor para: artículos, documentos sencillos


Motor Balanceado (Balanced)

Para documentos mixtos con texto e imágenes
Tiempo típico: 8-12 segundos
Mejor para: informes, presentaciones, documentos generales


Motor de Máxima Calidad (Quality)

Para documentos complejos o escaneados que requieren OCR
Tiempo típico: 15-25 segundos
Mejor para: libros, documentos escaneados, documentos técnicos con fórmulas



Configuración Avanzada
Personalización de Puertos
Modifica los valores en el archivo .env para cambiar los puertos:
envFRONTEND_PORT=3003    # Puerto para el frontend React
BACKEND_PORT=5175     # Puerto para la API Flask
NGINX_PORT=80         # Puerto para Nginx
Escalado de Workers
Para ajustar el número de workers de Celery y mejorar el rendimiento en conversiones paralelas:
yaml# En docker-compose.yml
worker:
  deploy:
    replicas: 4  # Ajusta según tus necesidades
Solución de Problemas
Problemas Comunes y Soluciones

Los contenedores no inician correctamente

bash   # Verificar logs
   docker-compose logs
   
   # Reiniciar servicios
   docker-compose restart

Error en la conversión de PDFs escaneados

Asegúrate de que el OCR esté correctamente configurado
Verifica que el documento escaneado tenga suficiente calidad


Problemas de permisos en volúmenes Docker

bash   # Corregir permisos
   sudo chown -R 1000:1000 ./backend/uploads ./backend/results
Roadmap

✅ Versión MVP con soporte básico PDF → EPUB
✅ Integración de OCR para documentos escaneados
✅ Análisis automático con IA
⏳ Vista previa EPUB integrada
⏳ Panel analytics con KPIs detallados
⏳ Optimizaciones rendimiento OCR
🔜 Sistema autenticación OAuth
🔜 Internacionalización (español, inglés, francés)

Contribuir

Haz un fork del repositorio
Crea una rama para tu función (git checkout -b feature/amazing-feature)
Haz commit de tus cambios (git commit -m 'Add amazing feature')
Push a la rama (git push origin feature/amazing-feature)
Abre un Pull Request

Licencia
MIT
Equipo

Desarrollado por el equipo Anclora
Contacto: equipo@anclora.com


Anclora PDF2EPUB - Parte del ecosistema Anclora para gestión y transformación inteligente de documentos digitales.
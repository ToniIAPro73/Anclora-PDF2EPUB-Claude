# Monitorización de Celery y Health Checks

Esta guía resume la nueva configuración de arquitectura aplicada en la Fase 1 para optimizar el rendimiento y observabilidad del backend.

## 1. Configuración de Celery centralizada

- La configuración vive en `backend/app/celery_app.py`.
- Variables principales controladas via `.env`:
  - `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
  - `CELERY_DEFAULT_QUEUE`, `CELERY_CONVERSION_QUEUE`
  - `CELERY_TASK_SOFT_TIME_LIMIT`, `CELERY_TASK_TIME_LIMIT`
  - `CELERY_MAX_RETRIES`, `CELERY_RETRY_BACKOFF`, `CELERY_RETRY_JITTER`
  - `CELERY_TASK_EXPIRES`
- Los workers se inician con `celery -A app.tasks worker --loglevel=info` (se mantiene compatibilidad).
- Las tareas usan `acks_late`, reintentos automáticos y métricas Prometheus.

## 2. Colas dedicadas por conversión

- El endpoint `POST /api/convert` envía las tareas a la cola configurada en `CELERY_CONVERSION_QUEUE`.
- Las tareas expiran pasado `CELERY_TASK_EXPIRES` segundos para evitar acumulación de jobs huérfanos.
- La respuesta de la API incluye la cola y expiración para depuración rápida.

## 3. Health check unificado

- Nuevo endpoint `GET /health`:
  - Revisa estado de configuración (`ConfigManager`), accesibilidad de carpetas (`uploads`, `results`, `thumbnails`) y estado del worker vía `celery control ping`.
  - Respuestas posibles: `ok` o `degraded`.
  - Se recomienda publicarlo detrás de autenticación básica o permitirlo solo desde balanceadores.

```json
{
  "status": "ok",
  "celery": "ok",
  "directories": {
    "uploads": true,
    "results": true,
    "thumbnails": true
  },
  "timestamp": "2025-09-17T05:38:00Z"
}
```

## 4. Métricas y observabilidad

- Los workers pueden exponer métricas Prometheus activando `WORKER_METRICS_PORT` en `.env`.
- `/metrics` sigue disponible para el servicio Flask; úsalo con autenticación o segmentación de red.
- Se recomienda añadir dashboards en Grafana para:
  - Latencia de tareas (`celery_task_duration_seconds`).
  - Conteo de conversiones (`pdf_conversions_total`).
  - Estado del health check (`/health`).

## 5. Pasos siguientes sugeridos

1. Añadir alerta cuando `/health` devuelva `degraded` durante más de 5 minutos.
2. Documentar comandos de despliegue para workers (systemd, docker-compose, etc.).
3. Configurar `flower` o Prometheus exporters para inspeccionar colas.

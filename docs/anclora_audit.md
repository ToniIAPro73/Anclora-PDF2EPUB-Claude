Informe Evaluación Integral Anclora PDF2EPUB

Contexto: Análisis técnico y de diseño respaldado por la guía de identidad visual (docs/design/Anclora_visual_identity_completo_mejorado.html) y revisión del repositorio completo (frontend, backend, infraestructura y tests).
1. Funcionalidad y Flujo de Usuario
Cobertura actual: Conversión PDF→EPUB con análisis previo, historial, descarga y vista previa; autenticación via Supabase; sistema de créditos básico.
Debilidades: Limpieza indiscriminada de Redis al iniciar cada conversión impide concurrencia multiusuario (backend/app/routes.py:80). Falta de gestión de reintentos y expiración de tareas, carencia de notificaciones de error en frontend y manejo del caso sin archivos previos.
Recomendaciones clave:
Aislar cola de tareas por usuario o por task-id; evitar r.delete global.
Implementar reintentos y expiración en Celery, con feedback visual en frontend.
Añadir seguimiento de estados intermedios (análisis, conversión, postproceso) y notificaciones al usuario.
2. Arquitectura General
Backend: Flask + Celery + Redis; métricas Prometheus; integración con Supabase. Genera app por tarea Celery (penaliza rendimiento). Config hardcoded en múltiples módulos.
Frontend: React 18 (TS) + Tailwind + i18n; estado distribuido en componentes; layout principal en App.tsx con secciones hero/panel/upload/chat.
Infraestructura: Docker-compose con servicios mínimos; falta documentación de despliegues, health-checks y pipeline CI/CD.
Riesgos: Duplica modelos (SQLAlchemy) y datos en Supabase sin sincronización; secretos en repositorio; métricas expuestas sin auth; sin plan de limpieza para uploads/, results/ y thumbnails/.
3. Base de Datos y Gestión de Datos
Modelado SQLAlchemy (backend/app/models.py): Conversion, User, CreditTransaction, PipelineCost, Referral.
Supabase (backend/app/supabase_client.py): Insert/Update/Select sobre tabla conversions; autenticación vía JWT.
Problemas: Convivencia de ORM local y Supabase sin replicación → inconsistencias. Falta de constraints (FK, unique, enums). No hay migraciones gestionadas (Alembic).
Acciones críticas:
Decidir fuente de verdad (Supabase vs Postgres propio); eliminar duplicidad.
Configurar versión de esquema y migraciones.
Añadir validaciones de estado y transacciones ACID para créditos.
4. Autenticación y Seguridad
Fortalezas: Decorador supabase_auth_required centraliza verificación; CORS configurado para entornos locales; limitador de peticiones global.
Debilidades: Logging imprime prefijos de tokens; fallback a cliente mock sin alertar; rate limit global en vez de por usuario; /metrics público; credenciales Redis hardcodeadas (routes.py).
Mejoras:
Sanitizar logs y centralizar secrets en .env + gestor (Vault).
Rate limiting por IP + user; proteger /metrics y endpoints admin con auth.
Implementar rotación de tokens y renovación automática en frontend.
5. Backend: Diseño y Rendimiento
Conversión (backend/app/tasks.py): Pipeline modular con métricas. Genera miniaturas con pdf2image.
Limitaciones: create_app() dentro de Celery; sin streaming de progreso; limpieza de tareas manual; sin control de tamaño máximo de PDF; no se manejan colas dedicadas por pipeline.
Optimización:
Reutilizar contexto Flask mediante app factory global en worker.
Usar apply_async con colas específicas; agregar acks_late, timeouts y retry.
Programar cleanup periódico y almacenamiento en S3/Cloud Storage para persistencia.
6. Frontend: UX, Responsive y Legibilidad
Identidad: Tipografías, paleta y gradientes alineados con guía (frontend/src/index.css); tokens definidos.
Desalineaciones: Iconografía placeholder (??, ?), héroe saturado; contraste insuficiente en modo claro; grid 12 columnas sin breakpoints → solapamiento en tablets; jerarquías tipográficas no siguen escala modular.
Recomendaciones:
Crear componentes reutilizables (Hero, Card, Panel) con tokens de la guía.
Ajustar breakpoints Tailwind, usar grid-cols-1/2 y flex-col en pantallas medias.
Definir sistema de iconos e ilustraciones acorde a identidad.
Añadir pruebas visuales y de accesibilidad (axe, Lighthouse).
Desacoplar estado global (Zustand/Context) y separar secciones (routes, pages).
7. Conectividad e Integraciones
Supabase: Uso de client oficial; falta manejo de errores (network, expiración token).
Redis / Celery: Config local; no se documenta setup en producción ni se exponen métricas de estado de workers.
Otros servicios: Prometheus/Grafana mencionados pero sin configuración en repo.
Acciones:
Documentar flujos de despliegue y docker-compose extendido.
Añadir endpoints de health-check (backend y worker).
Implementar reconexión en frontend (fetch con retry/backoff).
Evaluar WebSockets o Supabase Realtime para estado de tareas.
8. Testing y Observabilidad
Cobertura: Suites amplias para backend (validación, rutas, supabase, pipelines); tests integrados; mocks de Supabase. Frontend con tests mínimos (__tests__).
Gap: Falta E2E real (Cypress/Playwright), tests responsive, accesibilidad, performance. No hay pipeline CI documentado ni coverage report unificado.
Propuesta:
Introducir Playwright para flujo completo y snapshots responsivos.
Integrar linters y pruebas en CI (GitHub Actions).
Añadir pruebas de carga (Locust) y métricas RUM básicas.
Centralizar logs (ELK/OTel) y dashboards de forma reproducible.
9. Plan de Mejora Prioritizado
Fase 0 – Estabilidad y Seguridad (Alta)

Unificar almacenamiento (Supabase vs Postgres); eliminar duplicidades y definir migraciones.
Externalizar secrets y sanitizar logs (tokens, Redis).
Corregir limpieza de Redis: limitar a tareas del usuario/task-id.
Proteger /metrics, aplicar rate limit por usuario/IP y harden CORS según entorno.
Definir política de retención/limpieza de archivos (cron job, storage externo).
Fase 1 – Arquitectura y Rendimiento (Alta)

Optimizar Celery: colas dedicadas, reintentos, timeouts, reuso de app context.
Implementar seguimiento de progreso robusto (polling con backoff, WebSockets opcionales).
Documentar y automatizar despliegues (Docker Compose prod, health-checks).
Añadir pruebas E2E (Playwright) cubriendo flujo conversión completo.
Formalizar observabilidad: dashboards preconfigurados, alertas y logging centralizado.
Fase 2 – Experiencia de Usuario e Identidad (Media)

Refactorizar layout responsive conforme a design tokens; adecuar breakpoints y jerarquías.
Incorporar iconografía/ilustraciones oficiales y estados vacíos/feedback consistentes.
Crear librería de componentes (Storybook) alineada a la guía visual.
Reorganizar estado global (contextos especializados o Zustand) y rutas por secciones.
Mejorar contraste tipográfico y accesibilidad (WCAG AA).
Fase 3 – Conectividad y Modularidad (Media)

Crear SDK frontend para API (manejo de errores, autenticación, caching).
Documentar contratos backend (OpenAPI/Swagger) y versionado de API.
Integrar Supabase Functions/RPC para créditos y reportes.
Añadir health-checks externos y monitorización de workers (flower, Prometheus).
Fase 4 – Optimización Continua (Baja)

Pruebas de carga y estrés sobre pipeline de conversión; optimizar miniaturas y caching.
Automatizar pruebas de accesibilidad y regresión visual.
Explorar análisis incremental y cache de PDF para usuarios recurrentes.
Implementar pipeline CI/CD completo (build, tests, lint, deploy staging/prod).
10. Próximos Pasos Sugeridos
Decidir estrategia de datos (Supabase vs Postgres) y planificar migración.
Crear issues/tareas para Fase 0 y 1 con responsables claros.
Establecer baseline de métricas (tiempo conversión, tasa errores, Core Web Vitals).
Iniciar refactor de frontend siguiendo tokens y componentes definidos.
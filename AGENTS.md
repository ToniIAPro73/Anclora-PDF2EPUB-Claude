# Repository Guidelines

## Project Structure & Module Organization
- `backend/app/` hosts the Flask API, Celery tasks, and Supabase clients; configs sit in `config.py`.
- `frontend/src/` contains the Vite + React UI (components, hooks, i18n, styles); static assets live under `frontend/public/`.
- `tests/` merges service and integration specs (`tests/backend/`) with shared fixtures; React specs reside in `frontend/src/__tests__/`.
- `docs/` holds architecture and ops guides; update them alongside behavioral changes (automation helpers stay in `scripts/` and container overrides in `docker/`).

## Build, Test, and Development Commands
- `docker-compose up -d` from the repository root brings up Redis, the Flask API, and the Vite frontend behind the proxy.
- Local Python setup: `python -m venv venv-py311 && venv-py311\Scripts\activate && pip install -r backend/requirements.txt`.
- Backend dev server: `python backend/main.py`; Celery worker: `celery -A app.tasks.celery_app worker --pool=eventlet`.
- Frontend dev: `cd frontend && npm install && npm start`; production bundles use `npm run build`.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation and type hints; keep functions `snake_case` and classes `PascalCase`.
- Keep business logic in services (Supabase clients, converters, tasks) and expose thin route handlers in `routes.py`.
- React code uses TypeScript function components, 2-space indentation, single quotes, and file names like `ConversionPanel.tsx`.
- Prefer Tailwind tokens over ad-hoc CSS; shared overrides belong in `frontend/src/styles/`.

## Testing Guidelines
- `pytest` is the authoritative suite (see `.github/workflows/tests.yml`); target modules with `pytest tests/backend/test_routes.py` when iterating.
- Run `npm run test` for React specs in `frontend/src/__tests__/`; keep filenames in the `*.test.tsx` pattern.
- Add coverage for new pipelines with existing PDF fixtures and assert EPUB outputs in or near `tests/backend/test_converter.py`.

## Commit & Pull Request Guidelines
- Keep commit summaries short, sentence-case, and focused, matching history such as `Actualizacion documento` or `Improve visibility...`.
- Reference issues in the body (`Refs #123`) and note any docs, migrations, or environment changes.
- Confirm `pytest` and `npm run test` before opening a PR, and document the results plus screenshots for UI-facing work.
- PR descriptions should outline scope, deployment considerations, and must not include `.env`, `backend/app.db`, or generated PDF/EPUB assets.

## Security & Configuration Tips
- Bootstrap environments from `.env.example`, fill in Supabase keys, and rotate secrets via `scripts/generate-secrets.py`; never commit populated `.env` files.
- The Redis password baked into `scripts/start_dev.bat` is for local use; override it in production compose files or secrets managers.
- Enforce file validation through `backend/app/file_validator.py` and mirror new checks with tests in `tests/backend/test_file_validator.py`.

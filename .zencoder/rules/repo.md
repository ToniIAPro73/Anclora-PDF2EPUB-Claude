---
description: Repository Information Overview
alwaysApply: true
---

# Anclora PDF2EPUB Information

## Summary

Anclora PDF2EPUB is an intelligent PDF to EPUB3 document conversion system with integrated AI. It features multiple conversion engines (Rapid, Balanced, Quality), multilingual support (English and Spanish), and a cloud-ready architecture using Supabase for authentication and database services.

## Structure

- **backend/**: Python Flask API with PDF conversion logic
- **frontend/**: React/TypeScript web interface
- **docker/**: Docker configuration files
- **supabase/**: Supabase database setup scripts
- **scripts/**: Utility scripts for development and deployment
- **docs/**: Project documentation
- **tests/**: Integration tests
- **functions/**: Serverless functions

## Language & Runtime

**Backend**:

- **Language**: Python 3.11+
- **Framework**: Flask 3.0.3
- **Task Queue**: Celery 5.5.3 with Redis 6.1.1

**Frontend**:

- **Language**: TypeScript 5.2+
- **Framework**: React 18.2.0
- **Build Tool**: Vite 7.1.5

## Dependencies

### Backend Dependencies

**Main Dependencies**:

- Flask-SQLAlchemy, Flask-Migrate (Database ORM)
- PyMuPDF, EbookLib (PDF/EPUB handling)
- pytesseract, Pillow (OCR and image processing)
- camelot-py (Table extraction)
- supabase (Authentication and database)
- prometheus-client (Metrics)

### Frontend Dependencies

**Main Dependencies**:

- @supabase/supabase-js (Authentication)
- react-router-dom (Routing)
- i18next, react-i18next (Internationalization)
- tailwindcss (Styling)
- katex, mathjax (Math formula rendering)

## Build & Installation

```bash
# Clone repository
git clone https://github.com/ToniIAPro73/Anclora-PDF2EPUB-Claude.git
cd Anclora-PDF2EPUB-Claude

# Set up environment variables
cp .env.example .env
# Edit .env with Supabase credentials

# Start application with Docker
docker-compose up -d
```

## Docker

**Configuration**:

- **Backend**: Python 3.11 with tesseract-ocr
- **Frontend**: Node.js 18 with npm
- **Services**: Redis, Prometheus, Grafana
- **Orchestration**: Docker Compose

**Main Files**:

- `docker-compose.yml`: Production configuration
- `docker-compose.dev.yml`: Development configuration
- `docker/Dockerfile.backend`: Backend container
- `docker/Dockerfile.frontend`: Frontend container

## Testing

**Backend Testing**:

- **Framework**: pytest 7.4.3
- **Test Location**: `backend/tests/` and `tests/`
- **Run Command**:

```bash
cd backend
pytest
```

**Frontend Testing**:

- **Framework**: Vitest with jsdom
- **Test Location**: `frontend/src/__tests__/`
- **Run Command**:

```bash
cd frontend
npm test
```

## CI/CD

**GitHub Actions**:

- Workflow: `.github/workflows/tests.yml`
- Runs on: Ubuntu Latest
- Python version: 3.11
- Tests: pytest

## Database

**Type**: PostgreSQL (via Supabase)
**Setup**: SQL scripts in `supabase/` directory
**Authentication**: JWT-based with Supabase

## Monitoring

**Metrics**: Prometheus + Grafana
**Logging**: Structured JSON logs
**Endpoints**: `/metrics` for Prometheus scraping

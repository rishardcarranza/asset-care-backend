# Asset Care - Backend API

RESTful API for Asset Care (Personal Asset Maintenance Manager) built with FastAPI, SQLAlchemy 2.0, PostgreSQL (JSONB), and Alembic.

## Prerequisites
- Docker & Docker Compose

## Quickstart with Docker Compose

1. Clone or navigate to the repository:
   ```bash
   cd backend
   ```

2. Verify or edit environment variables:
   ```bash
   cp .env.example .env
   ```

3. Start services:
   ```bash
   docker compose up --build -d
   ```

4. Check API health:
   - Health endpoint: `http://localhost:8000/health`
   - Interactive Docs (Swagger): `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

5. Export OpenAPI specification for the mobile app:
   ```bash
   docker compose exec api poetry run python scripts/export_openapi.py
   ```

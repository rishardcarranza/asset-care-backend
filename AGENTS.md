# AGENTS.md - Backend (Asset Care API)

## 1. Scope & System Role
- **Application:** Asset Care (Personal Asset Maintenance Manager - Backend API).
- **Role:** RESTful API providing persistence, business logic validation, dynamic asset metadata management, and OpenAPI schema generation for client synchronization.
- **Contract Ownership:** This repository is the **single source of truth** for the API contract (`openapi.json`). Any schema or route changes must be reflected in the generated OpenAPI specification.

## 2. Technology Stack & Tooling
- **Runtime & Language:** Python 3.12+ with strict type hints throughout. Never use `Any`.
- **Framework:** FastAPI.
- **ORM & Migrations:** SQLAlchemy 2.0 (or SQLModel) with Alembic for database migrations.
- **Database:** PostgreSQL with native `JSONB` support.
- **Package Manager:** `Poetry` exclusively (`pyproject.toml`). Never use `pip` directly.
- **Containerization:** Docker & `docker-compose.yml` for local API and PostgreSQL orchestration.

## 3. Dynamic Data Architecture (JSONB)
- **Flexible Asset Schema:** The core `assets` table must use a PostgreSQL `JSONB` column to store heterogeneous attributes per asset type.
  - *Vehicles example:* `{"engine": "G4KE", "oil_type": "5W-20", "last_mileage": 85000, "mileage_unit": "km"}`
  - *HVAC / Appliances example:* `{"btu": 12000, "refrigerant": "R410A", "installation_date": "2023-05-10"}`
- **Validation Pipeline:**
  - Every dynamic payload must be rigorously validated using Pydantic models before being written to the database.
  - Define custom validators or discriminator models for each supported asset category.
- **Language-Neutral Enums & Identifiers:**
  - Database values, category names, maintenance types, and metric keys must always be stored in technical English / language-neutral identifiers (e.g., `oil_change`, `vehicle`, `hvac`, `filter_replacement`). Never store localized display text in database enums.
  - API error responses should provide standardized machine-readable error codes (e.g., `{"code": "ASSET_NOT_FOUND", "detail": "..."}`) to enable client-side localization.

## 4. Architecture & Layer Separation
Maintain strict separation of concerns across modules:
- `routers/`: Endpoint routing, request/response serialization, HTTP status codes, dependency injection.
- `schemas/`: Pydantic input/output transfer objects (DTOs) and validation schemas.
- `models/`: SQLAlchemy ORM / SQLModel database entities.
- `crud/` or `repositories/`: Pure database access methods and queries. No direct HTTP exceptions here.
- `services/`: Complex business logic (e.g., maintenance schedule calculation, threshold alerts).

## 5. API Contract & Workflow
- After modifying or creating endpoints, schemas, or models, ensure the `openapi.json` file is regenerated or accessible for the mobile frontend.
- Do not introduce breaking changes to existing endpoints without updating versioning or coordinating schema compatibility.

## 6. AI & Development Guidelines
- **Package Management:** Use `poetry add <package>` or `poetry run <cmd>`. Always inspect `pyproject.toml` before proposing new dependencies.
- **Intent-Driven Docstrings:** Explain the *why*, not just the *what*, especially in complex query filters, JSONB queries, and scheduling logic.
- **File Size Constraint:** Keep files modular. Refactor and decompose any file exceeding 200 lines.
- **Language:** Code identifiers, docstrings, technical comments, and git commit messages must be written in technical English.

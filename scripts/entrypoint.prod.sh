#!/usr/bin/env bash
set -e

echo "[Entrypoint] Waiting for PostgreSQL database to be ready..."
poetry run python - <<'EOF'
import os
import sys
import time
import psycopg2

db_url = os.environ.get("DATABASE_URL", "").strip()
if not db_url:
    pg_user = os.environ.get("POSTGRES_USER", "assetcare")
    pg_pass = os.environ.get("POSTGRES_PASSWORD", "assetcare_secret")
    pg_host = os.environ.get("POSTGRES_HOST", "asset_care_db")
    pg_db = os.environ.get("POSTGRES_DB", "assetcare_db")
    db_url = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:5432/{pg_db}"

# Convert SQLAlchemy driver prefix to standard libpq format for psycopg2
dsn = db_url.replace("postgresql+psycopg2://", "postgresql://")

max_retries = 30
for attempt in range(1, max_retries + 1):
    try:
        conn = psycopg2.connect(dsn)
        conn.close()
        print(f"[Entrypoint] PostgreSQL is ready (attempt {attempt}/{max_retries}).")
        sys.exit(0)
    except Exception as exc:
        print(f"[Entrypoint] Waiting for PostgreSQL ({attempt}/{max_retries}): {exc}")
        time.sleep(2)

print("[Entrypoint] ERROR: Could not connect to PostgreSQL after maximum retries.")
sys.exit(1)
EOF

echo "[Entrypoint] Running Alembic database migrations..."
poetry run alembic upgrade head

echo "[Entrypoint] Starting FastAPI production server..."
exec "$@"


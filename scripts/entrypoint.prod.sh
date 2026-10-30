#!/usr/bin/env bash
set -e

echo "[Entrypoint] Waiting for PostgreSQL database to be ready..."
poetry run python - <<'EOF'
import os
import sys
import time
import psycopg2

db_url = os.environ.get("DATABASE_URL", "")
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


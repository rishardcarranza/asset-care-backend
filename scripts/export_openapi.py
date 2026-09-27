"""Script to export FastAPI OpenAPI schema to openapi.json."""

import json
from pathlib import Path
import sys

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app


def export_openapi() -> None:
    """Generate and write OpenAPI JSON schema."""
    openapi_schema = app.openapi()

    # Paths: backend/openapi.json and root openapi.json
    backend_openapi_path = Path(__file__).resolve().parent.parent / "openapi.json"
    root_openapi_path = Path(__file__).resolve().parent.parent.parent / "openapi.json"

    with open(backend_openapi_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"Exported backend OpenAPI schema to: {backend_openapi_path}")

    with open(root_openapi_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"Exported shared OpenAPI schema to: {root_openapi_path}")


if __name__ == "__main__":
    export_openapi()

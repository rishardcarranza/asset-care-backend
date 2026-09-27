"""Tests for Offline-First delta pull and batch push synchronization."""

import uuid
from fastapi.testclient import TestClient


def test_sync_push_and_pull(client: TestClient) -> None:
    """Verify offline-created entity batch push and incremental pull."""
    offline_asset_id = str(uuid.uuid4())
    offline_rule_id = str(uuid.uuid4())

    push_payload = {
        "assets": [
            {
                "id": offline_asset_id,
                "name": "Warehouse Forklift",
                "asset_type": "vehicle",
                "description": "Electric 3-ton forklift",
                "metadata_payload": {"last_odometer": 1500.0, "odometer_unit": "km"},
                "updated_at": "2026-09-27T08:00:00Z",
                "is_deleted": False,
            }
        ],
        "maintenance_rules": [
            {
                "id": offline_rule_id,
                "asset_id": offline_asset_id,
                "maintenance_type": "hydraulic_fluid_check",
                "metric_type": "odometer",
                "interval_value": 250.0,
                "metric_unit": "km",
                "description": "Inspect hydraulic reservoir level",
                "updated_at": "2026-09-27T08:00:00Z",
                "is_deleted": False,
            }
        ],
        "maintenance_logs": [],
    }

    # 1. Execute push
    push_res = client.post("/api/v1/sync/push", json=push_payload)
    assert push_res.status_code == 200
    push_data = push_res.json()
    assert push_data["applied_assets"] == 1
    assert push_data["applied_rules"] == 1

    # 2. Verify asset is accessible
    asset_res = client.get(f"/api/v1/assets/{offline_asset_id}")
    assert asset_res.status_code == 200
    assert asset_res.json()["name"] == "Warehouse Forklift"

    # 3. Pull changes since 2026-09-27T00:00:00Z
    pull_res = client.get("/api/v1/sync/pull?since=2026-09-27T00:00:00Z")
    assert pull_res.status_code == 200
    pull_data = pull_res.json()
    asset_ids = [a["id"] for a in pull_data["assets"]]
    assert offline_asset_id in asset_ids

"""Tests for maintenance rules, logs, and preventive health scheduler."""

from fastapi.testclient import TestClient


def test_maintenance_scheduler_lifecycle(client: TestClient) -> None:
    """Test full cycle: asset -> rule -> overdue -> service log -> ok -> telemetry update -> due."""
    # 1. Create Vehicle with 50,000 km
    asset_res = client.post(
        "/api/v1/assets/",
        json={
            "name": "Delivery Van",
            "asset_type": "vehicle",
            "metadata_payload": {"last_odometer": 50000.0, "odometer_unit": "km"},
        },
    )
    assert asset_res.status_code == 201
    asset_id = asset_res.json()["id"]

    # 2. Add rule: Oil change every 5,000 km
    rule_res = client.post(
        "/api/v1/maintenance/rules",
        json={
            "asset_id": asset_id,
            "maintenance_type": "oil_change",
            "metric_type": "odometer",
            "interval_value": 5000,
            "metric_unit": "km",
            "description": "Engine oil and filter",
        },
    )
    assert rule_res.status_code == 201
    rule_id = rule_res.json()["id"]
    assert rule_id is not None

    # 3. Check health: No log recorded yet, so full odometer (50,000) exceeds 5,000 -> OVERDUE
    health_1 = client.get(f"/api/v1/assets/{asset_id}/health")
    assert health_1.status_code == 200
    report_1 = health_1.json()
    assert report_1["overall_status"] == "overdue"
    assert report_1["items"][0]["status"] == "overdue"

    # 4. Record service at 49,000 km
    log_res = client.post(
        "/api/v1/maintenance/logs",
        json={
            "asset_id": asset_id,
            "maintenance_type": "oil_change",
            "service_date": "2026-09-20T10:00:00Z",
            "metric_value_at_service": 49000,
            "cost": 50.00,
            "performed_by": "Fleet Garage",
        },
    )
    assert log_res.status_code == 201

    # 5. Check health: 50,000 - 49,000 = 1,000 km consumed out of 5,000 -> OK (20% used, 4000 left)
    health_2 = client.get(f"/api/v1/assets/{asset_id}/health")
    assert health_2.status_code == 200
    report_2 = health_2.json()
    assert report_2["overall_status"] == "ok"
    assert report_2["items"][0]["status"] == "ok"
    assert report_2["items"][0]["remaining_value"] == 4000.0
    assert report_2["items"][0]["percentage_used"] == 20.0

    # 6. Advance odometer to 53,600 km (4,600 km consumed / 5,000 = 92% -> DUE_SOON)
    client.put(
        f"/api/v1/assets/{asset_id}",
        json={"metadata_payload": {"last_odometer": 53600.0}},
    )

    health_3 = client.get(f"/api/v1/assets/{asset_id}/health")
    assert health_3.status_code == 200
    report_3 = health_3.json()
    assert report_3["overall_status"] == "due_soon"
    assert report_3["items"][0]["status"] == "due_soon"
    assert report_3["items"][0]["percentage_used"] == 92.0

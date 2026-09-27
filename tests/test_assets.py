"""Integration tests for Asset lifecycle and dynamic JSONB validation."""

from fastapi.testclient import TestClient


def test_system_health(client: TestClient) -> None:
    """Verify /health endpoint reports healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "Asset Care API"


def test_create_vehicle_with_dynamic_metadata(client: TestClient) -> None:
    """Verify creating a vehicle persists dynamic JSONB attributes."""
    payload = {
        "name": "Honda Civic 2018",
        "asset_type": "vehicle",
        "description": "Daily commuter sedan",
        "metadata_payload": {
            "engine": "2.0L K20C2",
            "oil_type": "0W-20",
            "last_odometer": 62000,
            "odometer_unit": "km",
            "transmission": "CVT",
        },
    }
    response = client.post("/api/v1/assets/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Honda Civic 2018"
    assert data["asset_type"] == "vehicle"
    assert data["metadata_payload"]["engine"] == "2.0L K20C2"
    assert data["metadata_payload"]["last_odometer"] == 62000.0
    assert data["is_deleted"] is False


def test_create_motorcycle_with_dynamic_metadata(client: TestClient) -> None:
    """Verify creating a motorcycle persists specialized motorcycle metadata."""
    payload = {
        "name": "Yamaha MT-07",
        "asset_type": "motorcycle",
        "description": "689cc naked sport bike",
        "metadata_payload": {
            "displacement_cc": 689,
            "drive_type": "chain",
            "cooling_type": "liquid",
            "engine": "CP2 Parallel-Twin",
            "oil_type": "10W-40 JASO MA2",
            "last_odometer": 12500,
            "odometer_unit": "km",
            "transmission": "6-speed",
        },
    }
    response = client.post("/api/v1/assets/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Yamaha MT-07"
    assert data["asset_type"] == "motorcycle"
    assert data["metadata_payload"]["displacement_cc"] == 689
    assert data["metadata_payload"]["drive_type"] == "chain"
    assert data["metadata_payload"]["cooling_type"] == "liquid"
    assert data["metadata_payload"]["oil_type"] == "10W-40 JASO MA2"
    assert data["metadata_payload"]["last_odometer"] == 12500.0


def test_get_asset_lifecycle(client: TestClient) -> None:
    """Verify GET, UPDATE and DELETE on an asset."""
    # Create asset
    create_res = client.post(
        "/api/v1/assets/",
        json={
            "name": "Office AC",
            "asset_type": "hvac",
            "metadata_payload": {"btu": 24000, "refrigerant": "R410A"},
        },
    )
    assert create_res.status_code == 201
    asset_id = create_res.json()["id"]

    # Read asset
    get_res = client.get(f"/api/v1/assets/{asset_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == asset_id

    # Update asset
    update_res = client.put(
        f"/api/v1/assets/{asset_id}",
        json={
            "name": "Office AC (Main Room)",
            "metadata_payload": {"filter_type": "HEPA-13"},
        },
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["name"] == "Office AC (Main Room)"
    # Check JSONB merge preserves previous btu while adding filter_type
    assert updated_data["metadata_payload"]["btu"] == 24000
    assert updated_data["metadata_payload"]["filter_type"] == "HEPA-13"

    # Soft delete asset
    del_res = client.delete(f"/api/v1/assets/{asset_id}")
    assert del_res.status_code == 204

    # Fetching deleted asset should return 404
    fetch_after_del = client.get(f"/api/v1/assets/{asset_id}")
    assert fetch_after_del.status_code == 404
    assert fetch_after_del.json()["error"]["code"] == "ASSET_NOT_FOUND"

"""Schemas package exporting all DTOs and validation models."""

from app.schemas.asset import (
    AssetBase,
    AssetCreate,
    AssetResponse,
    AssetUpdate,
)
from app.schemas.dynamic_metadata import (
    ApplianceMetadata,
    HVACMetadata,
    MotorcycleMetadata,
    OtherMetadata,
    VehicleMetadata,
    validate_metadata_payload,
)
from app.schemas.enums import (
    AssetType,
    MaintenanceStatus,
    MetricType,
)
from app.schemas.health import AssetHealthReport, MaintenanceHealthItem
from app.schemas.maintenance_log import (
    MaintenanceLogBase,
    MaintenanceLogCreate,
    MaintenanceLogResponse,
    MaintenanceLogUpdate,
)
from app.schemas.maintenance_rule import (
    MaintenanceRuleBase,
    MaintenanceRuleCreate,
    MaintenanceRuleResponse,
    MaintenanceRuleUpdate,
)

__all__ = [
    "AssetType",
    "MetricType",
    "MaintenanceStatus",
    "VehicleMetadata",
    "MotorcycleMetadata",
    "HVACMetadata",
    "ApplianceMetadata",
    "OtherMetadata",
    "validate_metadata_payload",
    "AssetBase",
    "AssetCreate",
    "AssetUpdate",
    "AssetResponse",
    "AssetHealthReport",
    "MaintenanceHealthItem",
    "MaintenanceRuleBase",
    "MaintenanceRuleCreate",
    "MaintenanceRuleUpdate",
    "MaintenanceRuleResponse",
    "MaintenanceLogBase",
    "MaintenanceLogCreate",
    "MaintenanceLogUpdate",
    "MaintenanceLogResponse",
]

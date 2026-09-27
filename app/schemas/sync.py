"""Pydantic schemas for Offline-First synchronization."""

from datetime import datetime
import uuid

from pydantic import BaseModel, Field

from app.schemas.asset import AssetResponse
from app.schemas.enums import AssetType, MetricType
from app.schemas.maintenance_log import MaintenanceLogResponse
from app.schemas.maintenance_rule import MaintenanceRuleResponse


class SyncPullResponse(BaseModel):
    """Payload sent to mobile client containing all entities modified since request timestamp."""

    synced_at: datetime
    assets: list[AssetResponse]
    maintenance_rules: list[MaintenanceRuleResponse]
    maintenance_logs: list[MaintenanceLogResponse]


class SyncAssetItem(BaseModel):
    """Asset mutation item submitted during push."""

    id: uuid.UUID
    name: str
    asset_type: AssetType
    description: str | None = None
    metadata_payload: dict = Field(default_factory=dict)
    updated_at: datetime
    is_deleted: bool = False


class SyncRuleItem(BaseModel):
    """Maintenance rule mutation item submitted during push."""

    id: uuid.UUID
    asset_id: uuid.UUID
    maintenance_type: str
    metric_type: MetricType
    interval_value: float
    metric_unit: str
    description: str | None = None
    updated_at: datetime
    is_deleted: bool = False


class SyncLogItem(BaseModel):
    """Maintenance log mutation item submitted during push."""

    id: uuid.UUID
    asset_id: uuid.UUID
    maintenance_type: str
    service_date: datetime
    metric_value_at_service: float | None = None
    cost: float | None = None
    notes: str | None = None
    performed_by: str | None = None
    updated_at: datetime
    is_deleted: bool = False


class SyncPushRequest(BaseModel):
    """Batch mutation payload uploaded by the mobile client."""

    assets: list[SyncAssetItem] = Field(default_factory=list)
    maintenance_rules: list[SyncRuleItem] = Field(default_factory=list)
    maintenance_logs: list[SyncLogItem] = Field(default_factory=list)


class SyncPushResponse(BaseModel):
    """Confirmation payload returned after processing sync mutations."""

    synced_at: datetime
    applied_assets: int
    applied_rules: int
    applied_logs: int

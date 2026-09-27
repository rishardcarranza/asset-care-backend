"""Pydantic schemas for MaintenanceRule entity."""

from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import MetricType


class MaintenanceRuleBase(BaseModel):
    """Shared properties for a maintenance interval rule."""

    maintenance_type: str = Field(
        ..., min_length=1, max_length=80, description="e.g. oil_change, air_filter"
    )
    metric_type: MetricType = Field(
        ..., description="Trigger metric: odometer, time_days, time_months, usage_hours"
    )
    interval_value: float = Field(
        ..., gt=0, description="Numerical interval (e.g. 5000, 180, 6)"
    )
    metric_unit: str = Field(
        ..., min_length=1, max_length=20, description="Measurement unit (e.g. km, mi, months)"
    )
    description: str | None = Field(default=None, description="Optional service notes")


class MaintenanceRuleCreate(MaintenanceRuleBase):
    """Payload to create a maintenance rule for an asset."""

    asset_id: uuid.UUID = Field(..., description="Target asset UUID")
    id: uuid.UUID | None = Field(
        default=None,
        description="Optional client-generated UUIDv4 (for offline-first creation)",
    )


class MaintenanceRuleUpdate(BaseModel):
    """Payload to modify a maintenance rule."""

    maintenance_type: str | None = Field(default=None, min_length=1, max_length=80)
    metric_type: MetricType | None = None
    interval_value: float | None = Field(default=None, gt=0)
    metric_unit: str | None = Field(default=None, min_length=1, max_length=20)
    description: str | None = None


class MaintenanceRuleResponse(MaintenanceRuleBase):
    """Response DTO for a maintenance rule."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

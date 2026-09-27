"""Pydantic schemas for MaintenanceLog entity."""

from datetime import datetime
from decimal import Decimal
import uuid

from pydantic import BaseModel, ConfigDict, Field


class MaintenanceLogBase(BaseModel):
    """Shared properties for an executed maintenance service log."""

    maintenance_type: str = Field(
        ..., min_length=1, max_length=80, description="e.g. oil_change, filter_swap"
    )
    service_date: datetime = Field(
        ..., description="UTC timestamp or ISO date of service execution"
    )
    metric_value_at_service: float | None = Field(
        default=None, ge=0, description="Odometer or usage hours at service time"
    )
    cost: Decimal | None = Field(
        default=None, ge=0, decimal_places=2, description="Service cost"
    )
    notes: str | None = Field(default=None, description="Observations, parts replaced")
    performed_by: str | None = Field(
        default=None, max_length=120, description="Technician or workshop name"
    )


class MaintenanceLogCreate(MaintenanceLogBase):
    """Payload to record an executed maintenance log."""

    asset_id: uuid.UUID = Field(..., description="Target asset UUID")
    id: uuid.UUID | None = Field(
        default=None,
        description="Optional client-generated UUIDv4 (for offline-first creation)",
    )


class MaintenanceLogUpdate(BaseModel):
    """Payload to modify a maintenance log entry."""

    maintenance_type: str | None = Field(default=None, min_length=1, max_length=80)
    service_date: datetime | None = None
    metric_value_at_service: float | None = Field(default=None, ge=0)
    cost: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    notes: str | None = None
    performed_by: str | None = Field(default=None, max_length=120)


class MaintenanceLogResponse(MaintenanceLogBase):
    """Response DTO for an executed maintenance log."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

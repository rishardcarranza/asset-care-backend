"""Schemas for asset health and maintenance status reporting."""

from datetime import datetime
import uuid

from pydantic import BaseModel, Field

from app.schemas.enums import MaintenanceStatus, MetricType


class MaintenanceHealthItem(BaseModel):
    """Health item describing the status of a specific maintenance rule."""

    rule_id: uuid.UUID
    maintenance_type: str
    metric_type: MetricType
    interval_value: float
    metric_unit: str
    current_reading: float = Field(
        ..., description="Current odometer or elapsed days/months"
    )
    last_service_date: datetime | None = None
    last_service_metric: float | None = None
    remaining_value: float = Field(
        ..., description="Remaining units before maintenance is due"
    )
    percentage_used: float = Field(
        ..., ge=0.0, description="Percentage of interval consumed (e.g. 95.0%)"
    )
    status: MaintenanceStatus


class AssetHealthReport(BaseModel):
    """Comprehensive health summary for an asset across all its rules."""

    asset_id: uuid.UUID
    asset_name: str
    overall_status: MaintenanceStatus
    rules_count: int
    items: list[MaintenanceHealthItem]

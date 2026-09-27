"""Pydantic schemas for Asset entity CRUD and API responses."""

from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import AssetType


class AssetBase(BaseModel):
    """Shared base properties for Asset."""

    name: str = Field(..., min_length=1, max_length=120, description="Asset display name")
    asset_type: AssetType = Field(..., description="Classification of the asset")
    description: str | None = Field(default=None, description="Optional notes or details")
    metadata_payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Category-specific dynamic attributes",
    )


class AssetCreate(AssetBase):
    """Payload to create an asset; accepts an optional client-generated UUID for offline creation."""

    id: uuid.UUID | None = Field(
        default=None,
        description="Optional client-generated UUIDv4 (for offline-first creation)",
    )


class AssetUpdate(BaseModel):
    """Payload to update an asset; all fields optional."""

    name: str | None = Field(default=None, min_length=1, max_length=120)
    asset_type: AssetType | None = None
    description: str | None = None
    metadata_payload: dict[str, Any] | None = None


class AssetResponse(AssetBase):
    """Response DTO for an asset."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

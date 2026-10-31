"""Pydantic schemas for dynamic asset metadata payloads."""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import AssetType


class BaseAssetMetadata(BaseModel):
    """Shared optional metadata attributes across all physical asset categories."""

    model_config = ConfigDict(extra="ignore")

    image_uri: str | None = Field(
        default=None,
        description="Filename or URI of the asset photo",
    )
    usage_hours: float | None = Field(
        default=None,
        ge=0.0,
        description="Cumulative operating hours for usage-based maintenance",
    )


class VehicleMetadata(BaseAssetMetadata):
    """Metadata schema for vehicles (cars, motorcycles, trucks)."""

    engine: str | None = Field(default=None, description="Engine model or displacement")
    oil_type: str | None = Field(default=None, description="Recommended motor oil grade")
    last_odometer: float = Field(
        default=0.0,
        ge=0.0,
        description="Last recorded odometer reading",
    )
    odometer_unit: str = Field(
        default="km",
        pattern="^(km|mi)$",
        description="Distance measurement unit",
    )
    license_plate: str | None = Field(default=None, description="Vehicle license plate")
    vin: str | None = Field(default=None, description="Vehicle Identification Number")
    transmission: str | None = Field(default=None, description="Manual or Automatic")


class MotorcycleMetadata(BaseAssetMetadata):
    """Metadata schema for motorcycles, scooters, and mopeds."""

    displacement_cc: int | None = Field(
        default=None,
        gt=0,
        description="Engine displacement in cubic centimeters (e.g. 250, 650)",
    )
    drive_type: str = Field(
        default="chain",
        pattern="^(chain|belt|shaft)$",
        description="Final drive mechanism: chain, belt, or shaft",
    )
    cooling_type: str = Field(
        default="air",
        pattern="^(air|liquid|oil)$",
        description="Engine cooling mechanism: air, liquid, or oil",
    )
    engine: str | None = Field(
        default=None, description="Engine model or architecture (e.g. Single, Twin, Inline-4)"
    )
    oil_type: str | None = Field(
        default=None, description="Motorcycle oil grade (e.g. 10W-40 JASO MA2)"
    )
    last_odometer: float = Field(
        default=0.0,
        ge=0.0,
        description="Last recorded odometer reading",
    )
    odometer_unit: str = Field(
        default="km",
        pattern="^(km|mi)$",
        description="Distance measurement unit",
    )
    license_plate: str | None = Field(default=None, description="Motorcycle license plate")
    vin: str | None = Field(default=None, description="Vehicle Identification Number")
    transmission: str | None = Field(
        default=None, description="Transmission type (e.g. 6-speed, Automatic)"
    )


class HVACMetadata(BaseAssetMetadata):
    """Metadata schema for heating, ventilation, and air conditioning."""

    btu: int | None = Field(default=None, gt=0, description="Cooling capacity in BTU/h")
    refrigerant: str | None = Field(default=None, description="Refrigerant gas type")
    filter_type: str | None = Field(default=None, description="Air filter model/specs")
    installation_date: str | None = Field(
        default=None, description="Date of physical installation (YYYY-MM-DD)"
    )


class ApplianceMetadata(BaseAssetMetadata):
    """Metadata schema for home/commercial appliances."""

    brand: str | None = Field(default=None, description="Manufacturer brand name")
    model_number: str | None = Field(default=None, description="Specific model number")
    serial_number: str | None = Field(default=None, description="Unit serial number")
    voltage: str | None = Field(default=None, description="Operating voltage (110V/220V)")
    warranty_until: str | None = Field(
        default=None, description="Warranty expiration date (YYYY-MM-DD)"
    )


class OtherMetadata(BaseAssetMetadata):
    """Metadata schema for uncategorized assets."""

    model_config = ConfigDict(extra="allow")

    notes: str | None = Field(default=None, description="Free-form technical notes")


METADATA_MODEL_MAP: dict[AssetType, type[BaseModel]] = {
    AssetType.VEHICLE: VehicleMetadata,
    AssetType.MOTORCYCLE: MotorcycleMetadata,
    AssetType.HVAC: HVACMetadata,
    AssetType.APPLIANCE: ApplianceMetadata,
    AssetType.OTHER: OtherMetadata,
}


def validate_metadata_payload(
    asset_type: AssetType, payload: dict[str, Any] | None
) -> dict[str, Any]:
    """Validate and normalize metadata payload against the designated asset type schema."""
    if payload is None:
        payload = {}

    model_cls = METADATA_MODEL_MAP.get(asset_type, OtherMetadata)
    validated = model_cls.model_validate(payload)
    return validated.model_dump(exclude_unset=False)

"""System enums for Asset Care (language-neutral identifiers)."""

from enum import Enum


class AssetType(str, Enum):
    """Categorization of supported asset classes."""

    VEHICLE = "vehicle"
    MOTORCYCLE = "motorcycle"
    HVAC = "hvac"
    APPLIANCE = "appliance"
    OTHER = "other"


class MetricType(str, Enum):
    """Types of metrics used to trigger maintenance thresholds."""

    ODOMETER = "odometer"
    TIME_DAYS = "time_days"
    TIME_MONTHS = "time_months"
    USAGE_HOURS = "usage_hours"


class MaintenanceStatus(str, Enum):
    """Calculated health status of an asset's maintenance task."""

    OK = "ok"
    DUE_SOON = "due_soon"
    OVERDUE = "overdue"

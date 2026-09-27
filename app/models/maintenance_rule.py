"""MaintenanceRule ORM model."""

from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Enum as SQLEnum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SyncBaseMixin
from app.schemas.enums import MetricType

if TYPE_CHECKING:
    from app.models.asset import Asset


class MaintenanceRule(Base, SyncBaseMixin):
    """Recurring maintenance threshold/rule configuration for an asset."""

    __tablename__ = "maintenance_rules"

    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    maintenance_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        index=True,
    )
    metric_type: Mapped[MetricType] = mapped_column(
        SQLEnum(MetricType, name="metric_type_enum"),
        nullable=False,
    )
    interval_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    metric_unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="rules")

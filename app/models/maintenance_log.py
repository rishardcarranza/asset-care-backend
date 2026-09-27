"""MaintenanceLog ORM model."""

from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import DateTime, Float, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SyncBaseMixin

if TYPE_CHECKING:
    from app.models.asset import Asset


class MaintenanceLog(Base, SyncBaseMixin):
    """Historical record of an executed maintenance service."""

    __tablename__ = "maintenance_logs"

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
    service_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    # Metric reading at time of service (e.g. 85000 km, or 1200 operating hours)
    metric_value_at_service: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    cost: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="logs")
